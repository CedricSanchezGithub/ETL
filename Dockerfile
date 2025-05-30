FROM python:3.10-slim
LABEL authors="cedric"

WORKDIR /app

# Copie du dossier Backend et des dépendances
COPY ./Backend /app/Backend
COPY ./requirements.txt /app/requirements.txt

# Installation des dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Exposition du port utilisé par Gunicorn
EXPOSE 5001

# Point d’entrée : on utilise Gunicorn pour lancer l'app Flask
CMD ["gunicorn", "--bind", "0.0.0.0:5001", "Backend.scheduler:app"]
