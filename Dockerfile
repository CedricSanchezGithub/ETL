FROM python:3.9-slim

LABEL authors="cedric"

# Installer les outils nécessaires
RUN apt-get update && apt-get install -y \
    build-essential \
    wget \
    vim

# Télécharger et installer Java
RUN wget https://download.java.net/openjdk/jdk11/ri/openjdk-11+28_linux-x64_bin.tar.gz || \
    (echo "Le lien est cassé déso ❤️ ➡️ trouver une autre source pour java 11" && exit 1) && \
    mkdir -p /usr/lib/jvm && \
    tar -xvf openjdk-11+28_linux-x64_bin.tar.gz -C /usr/lib/jvm && \
    rm openjdk-11+28_linux-x64_bin.tar.gz

# Configurer Java
ENV JAVA_HOME /usr/lib/jvm/jdk-11
ENV PATH $JAVA_HOME/bin:$PATH
ENV PATH="/home/jupyter/.local/bin:$PATH"

# Créer l'utilisateur non-root jupyter
RUN useradd -m -s /bin/bash jupyter && \
    mkdir -p /home/jupyter/workspace && \
    chown -R jupyter:jupyter /home/jupyter

# Mettre à jour pip
RUN pip install --no-cache-dir --upgrade pip

# Passer à l'utilisateur non-root
USER jupyter
WORKDIR /app

# Copier et installer les dépendances Python
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Installer JupyterLab
RUN pip install --no-cache-dir jupyterlab

# Vérifier l'installation de JupyterLab
RUN python3 -m pip show jupyterlab

# Exposer le port par défaut de Jupyter
EXPOSE 8888

# Lancer JupyterLab
CMD ["python3", "-m", "jupyter", "lab", "--ip=0.0.0.0", "--no-browser", "--allow-root", "--NotebookApp.token=''"]
