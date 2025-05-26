import datetime
import os

import pymysql
from flask import Blueprint, render_template, send_from_directory
from flask import request, jsonify

from Backend.config import DB_NAME, DB_PASSWORD, DB_USER, DB_HOST, IMAGES_DIR
from Backend.proxy.etl_proxy import trigger_etl, trigger_metadata

api = Blueprint("api", __name__)
photo_save = "Backend/static/photo_save"


@api.route("/")
def index():
    return "APScheduler est en cours d'exécution."


@api.route('/triggermspr')
def trigger_pipeline_etl():
    """
    Déclenche manuellement le pipeline ETL
    ---
    tags:
      - ETL
    responses:
      200:
        description: Pipeline ETL déclenchée avec succès
      500:
        description: Erreur lors du déclenchement
    """
    result = trigger_etl()
    return jsonify(result), 200 if result["success"] else 500

@api.route('/triggermetadata')
def trigger_pipeline_metadata():
    result = trigger_metadata()
    return jsonify(result), 200 if result["success"] else 500
    """
    Déclenche la génération ou mise à jour des métadonnées
    ---
    tags:
      - ETL
    responses:
      200:
        description: Pipeline metadata déclenchée avec succès
      500:
        description: Erreur lors du déclenchement
    """

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



@api.route("/images/<path:filename>")
def serve_image(filename):
    return send_from_directory(IMAGES_DIR, filename)
    """
    Sert une image statique depuis le dossier d’images
    ---
    tags:
      - Images
    parameters:
      - name: filename
        in: path
        type: string
        required: true
        description: Chemin de l'image à afficher
    responses:
      200:
        description: Image retournée
      404:
        description: Image non trouvée
    """

    return send_from_directory("static/images/augmented_train", filename)


@api.route("/api/images", methods=["GET"])
def get_images_by_species():
    """
    Images et informations d'une espèce
    ---
    tags:
      - Espèces
    parameters:
      - name: espece
        in: query
        type: string
        required: true
        description: Nom français de l'espèce
    responses:
      200:
        description: Métadonnées et images de l'espèce
      400:
        description: Paramètre 'espece' manquant
      404:
        description: Espèce introuvable
      500:
        description: Erreur serveur
    """

    espece = request.args.get("espece")
    if not espece:
        return jsonify({"error": "Paramètre 'espece' requis"}), 400

    try:
        conn = pymysql.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            charset="utf8mb4",
            cursorclass=pymysql.cursors.DictCursor,
        )

        with conn.cursor() as cursor:
            # Obtenir les métadonnées de l’espèce
            cursor.execute("SELECT * FROM wildlens_facts WHERE nom_fr = %s", (espece,))
            metadata = cursor.fetchone()
            if not metadata:
                return jsonify({"error": f"Espèce '{espece}' introuvable"}), 404

            id_espece = metadata["id_espece"]

            cursor.execute(
                "SELECT image FROM wildlens_images WHERE id_espece = %s", (id_espece,)
            )
            images = cursor.fetchall()

        conn.close()

        # Construire la réponse
        image_data = [
            {"path": img["image"], "url": f"/images/{img['image']}"} for img in images
        ]

        response = {
            "espece": espece,
            "nom_fr": metadata.get("nom_fr"),
            "nom_latin": metadata.get("nom_latin"),
            "description": metadata.get("description"),
            "population_estimee": metadata.get("population_estimee"),
            "localisation": metadata.get("localisation"),
            "nombre_image": metadata.get("nombre_image"),
            "images": image_data,
        }

        return jsonify(response)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api.route("/api/especes", methods=["GET"])
def get_especes():
    """
    Liste des espèces
    ---
    responses:
      200:
        description: Retourne une liste des espèces
        schema:
          type: object
          properties:
            especes:
              type: array
              items:
                type: string
    """
    try:
        conn = pymysql.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            charset="utf8mb4",
            cursorclass=pymysql.cursors.DictCursor,
        )

        with conn.cursor() as cursor:
            cursor.execute("SELECT nom_fr FROM wildlens_facts ORDER BY nom_fr ASC")
            rows = cursor.fetchall()

        conn.close()

        especes = [row["nom_fr"] for row in rows]
        return jsonify({"especes": especes})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api.route("/api/metadata", methods=["GET"])
def get_all_metadata():
    """
    Récupérer les métadonnées de toutes les espèces
    ---
    tags:
      - Espèces
    responses:
      200:
        description: Liste des métadonnées de chaque espèce
      500:
        description: Erreur serveur
    """

    try:
        conn = pymysql.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            charset="utf8mb4",
            cursorclass=pymysql.cursors.DictCursor,
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


@api.route("/interface")
def interface():
    """
    Interface HTML de test pour les fonctions ETL
    ---
    tags:
      - Interface
    responses:
      200:
        description: Interface HTML de gestion
    """

    return render_template("interface.html")


@api.route("/photo_download", methods=["POST"])
def photo_download():
    """
    Enregistrement d'une photo classée par le front
    ---
    tags:
      - Upload
    consumes:
      - multipart/form-data
    parameters:
      - name: file
        in: formData
        type: file
        required: true
        description: Image classée par le modèle TFLite
      - name: classification
        in: formData
        type: string
        required: false
        description: Nom de l'espèce détectée
    responses:
      200:
        description: Image enregistrée avec succès
      400:
        description: Erreur de validation ou type de fichier incorrect
      500:
        description: Erreur serveur lors de l’enregistrement
    """

    # Vérifier la présence du fichier
    if "file" not in request.files:
        return jsonify({"success": False, "message": "Aucun fichier trouvé"}), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"success": False, "message": "Aucun fichier sélectionné"}), 400

    # Vérification de l'extension
    allowed_extensions = {"jpg", "jpeg", "png"}
    if (
        "." not in file.filename
        or file.filename.rsplit(".", 1)[1].lower() not in allowed_extensions
    ):
        return jsonify({"success": False, "message": "Type de fichier non autorisé"}), 400

    # Récupérer la classification transmise
    classification = request.form.get("classification", "unknown").strip().replace(" ", "_")

    # Nom du fichier : wildlens_{classification}_{timestamp}.jpg
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    file_extension = file.filename.rsplit(".", 1)[1].lower()
    filename = f"wildlens_{classification}_{timestamp}.{file_extension}"

    # Enregistrement
    file_path = os.path.join(photo_save, filename)
    try:
        file.save(file_path)
        print(f"Image enregistrée : {filename} avec classification : {classification}")
    except Exception as e:
        return jsonify({"success": False, "message": "Erreur lors de l'enregistrement", "error": str(e)}), 500

    return jsonify(
        {
            "success": True,
            "message": f"Image classée comme '{classification}' enregistrée avec succès",
            "filename": filename,
            "classification": classification,
        }
    )
