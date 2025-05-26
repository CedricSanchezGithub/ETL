import os
import requests

ETL_BASE_URL = os.getenv("ETL_API_BASE_URL", "http://127.0.0.1:6001")

def trigger_etl():
    url = f"{ETL_BASE_URL}/triggermspr"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return {"success": True, "message": "ETL déclenchée avec succès"}
    except requests.RequestException as e:
        return {"success": False, "message": f"Erreur ETL: {e}"}

def trigger_metadata():
    url = f"{ETL_BASE_URL}/triggermetadata"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return {"success": True, "message": "Metadata déclenchée avec succès"}
    except requests.RequestException as e:
        return {"success": False, "message": f"Erreur metadata: {e}"}
