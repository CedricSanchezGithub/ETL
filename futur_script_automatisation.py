#!/usr/bin/env python3

from flask import Flask
from apscheduler.schedulers.background import BackgroundScheduler
import atexit
import logging

from ETL.futur_script_principal import script_principal

# Application Flask (optionnelle si vous voulez un endpoint HTTP)
app = Flask(__name__)

logging.basicConfig()
logging.getLogger('apscheduler').setLevel(logging.DEBUG)

def script_job():
    """Job appelé par APScheduler : lance le script principal."""
    script_principal()

@app.route('/')
def index():
    return "APScheduler est en cours d'exécution. Accès racine de l'application Flask."

@app.route('/scrape', methods=['GET'])
def trigger_scrape():
    """Endpoint pour déclencher le script principal manuellement."""
    script_job()
    return "Scraping déclenché manuellement."

if __name__ == '__main__':
    # Configuration d'APScheduler
    scheduler = BackgroundScheduler()
    # Planifie l'exécution du script principal tous les jours à 00:00
    scheduler.add_job(script_job, 'cron', hour=0, minute=0, id='daily_job')
    scheduler.start()

    # Arrêt propre du scheduler quand l'appli s'arrête
    atexit.register(lambda: scheduler.shutdown())

    # Lancement de l'appli Flask (sur port 5000 par défaut)
    app.run(host='0.0.0.0', port=5000, debug=True)