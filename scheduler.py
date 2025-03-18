#!/usr/bin/env python3

from flask import Flask
from apscheduler.schedulers.background import BackgroundScheduler
import atexit
import logging

from ETL.metadata_manager import create_metadata

# Application Flask (optionnelle si vous voulez un endpoint HTTP)
app = Flask(__name__)

from notebook_to_python import main_function

logging.basicConfig()
logging.getLogger('apscheduler').setLevel(logging.DEBUG)

def pipeline_etl_job():
    """Job appelé par APScheduler : lance le script principal du projet."""
    main_function()

@app.route('/')
def index():
    return "APScheduler est en cours d'exécution. Accès racine de l'application Flask."

@app.route('/triggermspr', methods=['GET'])
def trigger_pipeline_etl():
    print("Lancement de la pipeline via le endpoint /triggermspr")
    """Endpoint pour déclencher l'ETL manuellement."""
    pipeline_etl_job()
    return "Pipeline ETL déclenché manuellement."

@app.route('/triggermetadata', methods=['GET'])
def trigger_pipeline_metadata():
    """Endpoint pour déclencher l'ETL manuellement."""
    create_metadata()
    return "Pipeline ETL déclenché manuellement."

if __name__ == '__main__':
    # Configuration d'APScheduler
    scheduler = BackgroundScheduler()
    # Planifie l'exécution de 'pipeline_etl_job' tous les jours à 00:00
    scheduler.add_job(pipeline_etl_job, 'cron', hour=0, minute=0, id='daily_etl')
    scheduler.start()

    # Arrêt propre du scheduler quand l'appli s'arrête
    atexit.register(lambda: scheduler.shutdown())

    # Lancement de l'appli Flask (sur port 5000 par défaut)
    app.run(host='0.0.0.0', port=5000, debug=True)
