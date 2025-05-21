# Installation d'un Environnement Virtuel et des Dépendances en Local

### Créer un environnement virtuel
```bash
python3 -m venv env && source env/bin/activate
```
---
### Lancer la base de données mysql 
```bash
docker compose up
```
---
### Accéder à phpmyadmin 
http://localhost:8080   

---

### JDK pour java 11 sur Linux   
https://download.java.net/openjdk/jdk11/ri/openjdk-11+28_linux-x64_bin.tar.gz  

### Choisir sa version de java sur Linux
```bash
sudo update-alternatives --config java
```

### Drivers mysql sur Linux 
https://dev.mysql.com/get/Downloads/Connector-J/mysql-connector-j-9.1.0.zip