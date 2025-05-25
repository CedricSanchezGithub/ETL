import os
from dotenv import load_dotenv

load_dotenv()


def get_env_var(var_name: str) -> str:
    value = os.getenv(var_name)
    if not value:
        raise ValueError(f"❌ La variable d'environnement {var_name} est manquante.")
    return value

# Chemins
IMAGES_DIR = get_env_var("IMAGES_DIR_CONTAINER")

# Base de données
DB_HOST = get_env_var("DB_HOST")
DB_USER = get_env_var("DB_USER")
DB_PASSWORD = get_env_var("DB_PASSWORD")
DB_NAME = get_env_var("DB_NAME")
