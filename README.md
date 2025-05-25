# MSPR 2024 - 2025

### Cédric Sanchez - Valentin Fiess - Jason TCHAGA - Louis GARDET ###

### Mise en place du projet

git pull https://github.com/CedricSanchezGithub/ETL/edit/reorganisation   
docker compose up   
-m venv .venv  
source .venv/bin/activate

puis lancer main.py

### Interface de Contrôle

http://127.0.0.1:5001/interface

### Grafana

http://localhost:3001/
admin admin lors de la première connexion sur Grafana

### Backend

# Build l'image
docker build -t backend-wildlens -f Dockerfile .

# Lance le conteneur
docker run --env-file .env backend-wildlens

📌 Routes disponibles

Déclenchement des pipelines

    GET http://127.0.0.1:5000/triggermspr
    Déclenche manuellement le pipeline ETL principal.

    GET http://127.0.0.1:5000/triggermetadata
    Déclenche manuellement la génération des métadonnées.

Accès aux images

    GET http://127.0.0.1:5000/images/<filename>
    Sert une image spécifique depuis le dossier static/images/augmented_train.

    GET http://127.0.0.1:5000/api/images?espece=<nom_en>
    Retourne les images et métadonnées associées à une espèce donnée (paramètre espece requis).

Métadonnées

    GET http://127.0.0.1:5000/api/especes
    Retourne la liste des noms d’espèces (nom_en) disponibles dans la base.

    GET http://127.0.0.1:5000/api/metadata
    Retourne les métadonnées complètes pour toutes les espèces.