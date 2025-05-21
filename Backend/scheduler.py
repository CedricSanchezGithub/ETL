#!/usr/bin/env python3
from ETL.notebook_to_python import main_function


import atexit
import logging

from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask

from Backend.routes import api

# Application Flask
app = Flask(__name__)
# routes
app.register_blueprint(api)

logging.basicConfig()
logging.getLogger("apscheduler").setLevel(logging.DEBUG)


def pipeline_etl_job():
    """Job appelé par APScheduler : lance le script principal du projet."""
    main_function()


if __name__ == "__main__":
    # Configuration d'APScheduler
    scheduler = BackgroundScheduler()
    # Planifie l'exécution de 'pipeline_etl_job' tous les jours à 00:00
    scheduler.add_job(pipeline_etl_job, "cron", hour=0, minute=0, id="daily_etl")
    scheduler.start()

    # Arrêt propre du scheduler quand l'appli s'arrête
    atexit.register(lambda: scheduler.shutdown())

    # Lancement de l'appli Flask (sur port 5000 par défaut)
    app.run(host="0.0.0.0", port=5000, debug=True)
