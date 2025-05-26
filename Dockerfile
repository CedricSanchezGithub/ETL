FROM python:3.10-slim
LABEL authors="cedric"

WORKDIR /app

# Copie du dossier Backend et des dépendances
COPY ./Backend /app/Backend
COPY ./requirements.txt /app/requirements.txt

# Installation des dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Point d’entrée : on lance scheduler.py
CMD ["python", "Backend/scheduler.py"]
