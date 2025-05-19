from threading import Thread

import pymysql
from flask import Blueprint, render_template, send_from_directory
from flask import request, jsonify

from ETL.metadata_manager import create_metadata
from ETL.notebook_to_python import main_function

api = Blueprint('api', __name__)


@api.route('/')
def index():
    return "APScheduler est en cours d'exécution."


@api.route('/triggermspr')
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


@api.route('/triggermetadata')
def trigger_pipeline_metadata():
    try:
        def run_metadata():
            try:
                create_metadata()
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


@api.route('/images/<path:filename>')
def serve_image(filename):
    return send_from_directory('static/images/augmented_train', filename)


@api.route('/api/images', methods=['GET'])
def get_images_by_species():
    espece = request.args.get("espece")
    if not espece:
        return jsonify({"error": "Paramètre 'espece' requis"}), 400

    try:
        # Connexion MySQL
        conn = pymysql.connect(
            host='localhost',
            user='root',
            password='root',
            database='wildlens',
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )

        with conn.cursor() as cursor:
            # Obtenir les métadonnées de l’espèce
            cursor.execute("SELECT * FROM wildlens_facts WHERE nom_en = %s", (espece,))
            metadata = cursor.fetchone()
            if not metadata:
                return jsonify({"error": f"Espèce '{espece}' introuvable"}), 404

            id_espece = metadata['id_espece']

            # Obtenir les images
            cursor.execute("SELECT image FROM wildlens_images WHERE id_espece = %s", (id_espece,))
            images = cursor.fetchall()

        conn.close()

        # Construire la réponse
        image_data = [{
            "path": img['image'],
            "url": f"/images/{img['image']}"
        } for img in images]

        response = {
            "espece": espece,
            "nom_fr": metadata.get("nom_fr"),
            "nom_latin": metadata.get("nom_latin"),
            "description": metadata.get("description"),
            "population_estimee": metadata.get("population_estimee"),
            "localisation": metadata.get("localisation"),
            "nombre_image": metadata.get("nombre_image"),
            "images": image_data
        }

        return jsonify(response)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api.route('/api/especes', methods=['GET'])
def get_especes():
    try:
        conn = pymysql.connect(
            host='localhost',
            user='root',
            password='root',
            database='wildlens',
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )

        with conn.cursor() as cursor:
            cursor.execute("SELECT nom_en FROM wildlens_facts ORDER BY nom_en ASC")
            rows = cursor.fetchall()

        conn.close()

        especes = [row["nom_en"] for row in rows]
        return jsonify({"especes": especes})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api.route('/api/metadata', methods=['GET'])
def get_all_metadata():
    try:
        conn = pymysql.connect(
            host='localhost',
            user='root',
            password='root',
            database='wildlens',
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )

        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT id_espece, nom_en, nom_fr, nom_latin, description,
                       population_estimee, localisation
                FROM wildlens_facts
                ORDER BY nom_en ASC
            """)
            rows = cursor.fetchall()

        conn.close()
        return jsonify({"metadata": rows})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api.route('/interface')
def interface():
    return render_template('interface.html')
