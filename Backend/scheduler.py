#!/usr/bin/env python3
import sys
sys.path.append("/app")

from Backend.proxy.etl_proxy import trigger_etl

import atexit
import logging

from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask
import time
import pymysql
from Backend.config import DB_HOST, DB_USER, DB_PASSWORD, DB_NAME
from Backend.routes import api
from flasgger import Swagger

# Application Flask
app = Flask(__name__)
swagger = Swagger(app)

# routes
app.register_blueprint(api)

logging.basicConfig()
logging.getLogger("apscheduler").setLevel(logging.DEBUG)

def pipeline_etl_job():
    result = trigger_etl()
    print(result["message"])

def test_mysql_connection(retries=5, delay=5):
    for attempt in range(1, retries + 1):
        try:
            conn = pymysql.connect(
                host=DB_HOST,
                user=DB_USER,
                password=DB_PASSWORD,
                database=DB_NAME,
                connect_timeout=5
            )
            conn.close()
            print("✅ Connexion MySQL réussie.")
            return
        except Exception as e:
            print(f"⚠️ Tentative {attempt}/{retries} échouée : {e}")
            if attempt < retries:
                print(f"⏳ Nouvelle tentative dans {delay} secondes...")
                time.sleep(delay)
            else:
                print("❌ Toutes les tentatives de connexion MySQL ont échoué. Arrêt du service.")
                exit(1)

# Initialisation exécutée à l'import du module (utile pour Gunicorn)
test_mysql_connection()

scheduler = BackgroundScheduler()
scheduler.add_job(pipeline_etl_job, "cron", hour=0, minute=0, id="daily_etl")
scheduler.start()
atexit.register(lambda: scheduler.shutdown())

# Exécution uniquement en local
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
