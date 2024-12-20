
import sys
import traceback

PYDEV_COMMAND_PREFIX = "# pydev_util_command"


def update_cell_name(cell_info, new_name):
    latest_cell_id = cell_info.latest_cell_id
    if latest_cell_id != 0:
        cell_info.jupyter_cell_id_to_name[latest_cell_id] = new_name
        cell_info.jupyter_cell_name_to_id[new_name] = latest_cell_id


def is_util_command(args, kwargs):
    """
    Check if command is a util command for Jupyter debugger, i.e. cell code starts with PYDEV_COMMAND_PREFIX
    This method relies on the signature IPython.core.compilerop.CachingCompiler.cache(code, number=0) in IPython 7
    """
    code = ""
    if len(args) > 0:
        code = args[0]
    else:
        if "code" in kwargs:
            code = kwargs["code"]
    if code.startswith(PYDEV_COMMAND_PREFIX):
        return True
    return False


def compile_cache_wrapper(orig, ipython_shell):
    def compile_cache(*args, **kwargs):
        cache_name = orig(*args, **kwargs)
        if is_util_command(args, kwargs):
            ipython_shell.pydev_cell_info.util_cell_names[cache_name] = True
            return orig(*args, **kwargs)
        update_cell_name(ipython_shell.pydev_cell_info, cache_name)
        return cache_name
    return compile_cache


def patch_compile_cache(ipython_shell):
    ipython_shell.compile.cache = compile_cache_wrapper(ipython_shell.compile.cache, ipython_shell)


class DebugCellInfo(object):
    latest_cell_id = 0
    jupyter_cell_id_to_name = {}
    jupyter_cell_name_to_id = {}
    util_cell_names = {}


def remove_imported_pydev_package():
    """
    Some third-party libraries might contain sources of PyDev and its modules' names will shadow PyCharm's
    helpers modules. If `pydevd` was imported from site-packages, we should remove it and all its submodules and
    re-import again (with proper sys.path)
    """
    pydev_module = sys.modules.get('pydevd', None)
    if pydev_module is not None and 'site-packages' in str(pydev_module):
        import os
        pydev_dir = os.listdir(os.path.dirname(pydev_module.__file__))
        pydev_dir.append('pydevd')
        imported_modules = set(sys.modules.keys())
        for imported_module in imported_modules:
            for dir in pydev_dir:
                if imported_module.startswith(dir):
                    sys.modules.pop(imported_module, None)


def attach_to_debugger(debugger_port):
    ipython_shell = get_ipython()

    import pydevd
    from _pydev_bundle import pydev_localhost

    debugger = pydevd.PyDB()
    debugger.frame_eval_func = None
    ipython_shell.debugger = debugger
    try:
        debugger.connect(pydev_localhost.get_localhost(), debugger_port)
        debugger.prepare_to_run(enable_tracing_from_start=False)
    except:
        traceback.print_exc()
        sys.stderr.write('Failed to connect to target debugger.\n')

    # should be executed only once for kernel
    if not hasattr(ipython_shell, "pydev_cell_info"):
        ipython_shell.pydev_cell_info = DebugCellInfo()
        patch_compile_cache(ipython_shell)
    # save link in debugger for quick access
    debugger.cell_info = ipython_shell.pydev_cell_info
    debugger.cell_info.util_cell_names = {}
    debugger.warn_once_map = {}


def set_latest_cell_id(latest_cell_id):
    ipython_shell = get_ipython()
    ipython_shell.pydev_cell_info.latest_cell_id = latest_cell_id


def enable_tracing():
    debugger = get_ipython().debugger
    # SetTrace should be enough, because Jupyter creates new frame every time
    debugger.enable_tracing()
    # debugger.enable_tracing_in_frames_while_running()


def remove_invalid_ids(valid_ids):
    cell_info = get_ipython().pydev_cell_info
    available_ids = list(cell_info.jupyter_cell_id_to_name.keys())
    for id in available_ids:
        if id not in valid_ids:
            cell_name = cell_info.jupyter_cell_id_to_name.pop(id)
            cell_info.jupyter_cell_name_to_id.pop(cell_name)


def disable_tracing():
    ipython_shell = get_ipython()
    ipython_shell.pydev_cell_info.latest_cell_id = 0
    if hasattr(ipython_shell, "debugger"):
        ipython_shell.debugger.disable_tracing()
        kill_pydev_threads(ipython_shell.debugger)


def kill_pydev_threads(py_db):
    from _pydevd_bundle.pydevd_kill_all_pydevd_threads import kill_all_pydev_threads
    py_db.finish_debugging_session()
    kill_all_pydev_threads()
