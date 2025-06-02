from flask import Flask, jsonify
from threading import Thread

from ETL.metadata_manager_new import metadata_manager
from notebook_to_python import main_function
from metadata_manager import create_metadata

app = Flask(__name__)

@app.route("/triggermspr")
def trigger_pipeline_etl():
    try:
        def run_pipeline():
            try:
                main_function()
            except Exception as e:
                print(f"[❌ ERREUR ETL] {e}")

        Thread(target=run_pipeline).start()

        return jsonify({
            "message": "✅ Pipeline ETL déclenchée avec succès.",
            "status": "started"
        }), 200

    except Exception as e:
        return jsonify({
            "message": "❌ Échec du déclenchement de la pipeline.",
            "error": str(e)
        }), 500


@app.route("/triggermetadata")
def trigger_pipeline_metadata():
    try:
        def run_metadata():
            try:
                metadata_manager()
            except Exception as e:
                print(f"[❌ ERREUR METADATA] {e}")

        Thread(target=run_metadata).start()

        return jsonify({
            "message": "✅ Pipeline Metadata déclenchée avec succès.",
            "status": "started"
        }), 200

    except Exception as e:
        return jsonify({
            "message": "❌ Échec du déclenchement de la pipeline Metadata.",
            "error": str(e)
        }), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=6001)
