FROM python:3.9-slim

LABEL authors="cedric"

# Installer les outils nécessaires
RUN apt-get update && apt-get install -y \
    build-essential \
    wget \
    unzip && \
    # Télécharger et installer OpenJDK 11
    wget https://download.java.net/openjdk/jdk11/ri/openjdk-11+28_linux-x64_bin.tar.gz && \
    mkdir -p /usr/lib/jvm && \
    tar -xvf openjdk-11+28_linux-x64_bin.tar.gz -C /usr/lib/jvm && \
    rm -f openjdk-11+28_linux-x64_bin.tar.gz && \
    # Télécharger et installer le connecteur MySQL
    wget https://dev.mysql.com/get/Downloads/Connector-J/mysql-connector-j-9.1.0.zip -P /tmp && \
    unzip /tmp/mysql-connector-j-9.1.0.zip -d /tmp && \
    mkdir -p /usr/lib/jvm/jars/ && \
    mv /tmp/mysql-connector-j-9.1.0/mysql-connector-j-9.1.0.jar /usr/lib/jvm/jars/ && \
    rm -rf /tmp/mysql-connector-j-9.1.0* && \
    # Nettoyer les outils
    apt-get remove -y wget unzip && apt-get autoremove -y && apt-get clean

# Configurer Java
ENV JAVA_HOME /usr/lib/jvm/jdk-11
ENV PATH $JAVA_HOME/bin:$PATH

# Copier et installer les dépendances Python
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r /app/requirements.txt

# Créer l'utilisateur non-root jupyter
RUN useradd -m -s /bin/bash jupyter && \
    mkdir -p /home/jupyter/workspace && \
    chown -R jupyter:jupyter /home/jupyter

USER jupyter
WORKDIR /home/jupyter/workspace

# Exposer le port par défaut de Jupyter
EXPOSE 8888

# Lancer JupyterLab
CMD ["python3", "-m", "jupyter", "lab", "--ip=0.0.0.0", "--no-browser", "--allow-root", "--NotebookApp.token=''"]
