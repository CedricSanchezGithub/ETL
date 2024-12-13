# MSPR 2024 - 2025
<<<<<<< HEAD
### Cédric Sanchez - Valentin Fiess - Jason TCHAGA - Louis GARDET ###
=======
### Cédric Sanchez - Valentin Fiess - Jason TCHAGA - Louis NECTOUX ###


------



Tutoriel : Configuration Docker + PyCharm avec JupyterLab
---

#### Étape 1 : Build et lancement du conteneur Docker

Build du conteneur Docker :
docker build -t python-data-env .

Lancer le conteneur Docker :
docker run --name python-data-env -p 8888:8888 -v $(pwd):/app -it python-data-env

---

#### Étape 2 : Configuration dans PyCharm

Ajouter une configuration Docker dans PyCharm :
Allez dans File > Settings > Project > Python Interpreter.
Cliquez sur l’icône d’engrenage, puis sur Add Interpreter.
Sélectionnez Docker comme environnement.

Configurer l’interpréteur Docker :
Docker server : sélectionnez votre configuration Docker (par exemple, Unix socket).
Image : choisissez l’image python-data-env que vous avez créée.
Validez les paramètres.

Configurer JupyterLab dans PyCharm :
Lancez PyCharm et ouvrez Settings > Jupyter.
Dans la section Jupyter Servers, ajoutez une nouvelle URL de serveur : http://127.0.0.1:8888/lab.
Validez la configuration.

---

#### Étape 3 : Test et utilisation

Vérifier l’accès à JupyterLab :
Une fois le conteneur démarré, accédez à JupyterLab via http://127.0.0.1:8888/lab dans votre navigateur.

Lancer un notebook dans PyCharm :
Cliquez avec le bouton droit sur un fichier .ipynb, puis sélectionnez Run File in Jupyter Notebook.
Vérifiez que l’environnement utilise bien le serveur configuré.

---
>>>>>>> 52f2ec4 (Update README.md)
