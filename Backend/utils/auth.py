import os
import functools
from flask import request, jsonify

def require_api_key(view_func):
    @functools.wraps(view_func)
    def wrapped(*args, **kwargs):
        api_key = os.environ.get("API_KEY")
        auth_header = request.headers.get("Authorization", "")
        if not api_key or not auth_header.startswith("Bearer "):
            return jsonify({"error": "Unauthorized"}), 401
        token = auth_header.split(" ", 1)[1]
        if token != api_key:
            return jsonify({"error": "Invalid API key"}), 403
        return view_func(*args, **kwargs)
    return wrapped
