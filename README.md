# MSPR 2024 - 2025

### Cédric Sanchez - Valentin Fiess - Jason TCHAGA - Louis GARDET ###

---
### Installation d'un Environnement Virtuel et des Dépendances en Local
```bash
-m venv .venv  
```
```bash
source .venv/bin/activate
```
```bash
pip install -r requirements.txt
```
---
### Interface de Contrôle

http://127.0.0.1:5001/interface

### Grafana

http://localhost:3001/  
admin admin lors de la première connexion sur Grafana

---
# Backend

### Lancer le backend
Lancer le 'proxy' pour l'ETL :   
```bash
gunicorn --bind 0.0.0.0:6001 ETL/serveur_etl:app
```
Lancer l'API principale :
```bash
 docker compose up --build
```
### Créer un fichier .env à la racine du projet avec les variables d'environnement nécessaires

```env
##### Clés API #####
mistral_api_key=""
gemini_api_key=""

##### Répertoires d’images (chemin absolu)  #####
IMAGES_DIR_CONTAINER=/app/Backend/static/images <- ne pas modifier
IMAGES_DIR_HOST=/chemin/vers/images/sur/hote

##### Base de données #####
DB_HOST=mysql-container
DB_USER=root
DB_PASSWORD=""
DB_NAME=wildlens

##### API ETL #####
ETL_API_BASE_URL=http://<ip_de_l_hote>:6001 <- c'est l'ip de votre machine hôte, pas celle du conteneur

```

----
# Docker 

### Se connecter au registre Docker (si besoin)
```bash
docker login
```
### Construire l'image Docker pour le backend
```bash
docker build -t cedsanc/backend-wildlens:1.3.8 . &&  docker build -t cedsanc/backend-wildlens:latest .
```
### Pousser l'image vers le registre Docker (changez le nom d'utilisateur par le votre si vous voulez)
```bash
docker push cedsanc/backend-wildlens:1.3.8 &&  docker push cedsanc/backend-wildlens:latest 
```

----

📌 Routes disponibles

Déclenchement des pipelines

    GET http://127.0.0.1:5001/triggermspr
    Déclenche le proxy qui déclanchera la pipeline ETL.

    GET http://127.0.0.1:6001/triggermspr
    Déclenche manuellement le pipeline ETL principal.

    GET http://127.0.0.1:5001/triggermetadata
    Déclenche le proxy qui déclanchera la génération des métadonnées.

    GET http://127.0.0.1:6001/triggermetadata
    Déclenche manuellement la génération des métadonnées.
    

Accès aux images

    GET http://127.0.0.1:5001/images/<filename>
    Sert une image spécifique depuis le dossier static/images/augmented_train.

    GET http://127.0.0.1:5001/api/images?espece=<nom_fr>
    Retourne les images et métadonnées associées à une espèce donnée (paramètre espece requis).

Métadonnées

    GET http://127.0.0.1:5001/api/especes
    Retourne la liste des noms d’espèces (nom_fr) disponibles dans la base.

    GET http://127.0.0.1:5001/api/metadata
    Retourne les métadonnées complètes pour toutes les espèces.