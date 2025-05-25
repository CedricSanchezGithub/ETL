# MSPR 2024 - 2025

### Cédric Sanchez - Valentin Fiess - Jason TCHAGA - Louis GARDET ###

### Mise en place du projet

git pull https://github.com/CedricSanchezGithub/ETL
docker compose up   

# Installation d'un Environnement Virtuel et des Dépendances en Local
-m venv .venv  
source .venv/bin/activate
pip install -r requirements.txt

# Installation de Java 11
sudo apt install openjdk-11-jdk


### Interface de Contrôle

http://127.0.0.1:5001/interface

### Grafana

http://localhost:3001/
admin admin lors de la première connexion sur Grafana

### Backend

# Se connecter au registre Docker
docker login

# Créer un fichier .env à la racine du projet avec les variables d'environnement nécessaires
# Exemple de contenu du fichier .env
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

# Construire l'image Docker pour le backend
docker build -t cedsanc/backend-wildlens:1.3.8 . &&  docker build -t cedsanc/backend-wildlens:latest .

# Pousser l'image vers le registre Docker (changez le nom d'utilisateur par le votre si vous voulez)
docker push cedsanc/backend-wildlens:1.3.8 &&  docker push cedsanc/backend-wildlens:latest 

# Lancer le docker compose
docker compose up 
📌 Routes disponibles

Déclenchement des pipelines

    GET http://127.0.0.1:5001/triggermspr
    Déclenche manuellement le pipeline ETL principal.

    GET http://127.0.0.1:5001/triggermetadata
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