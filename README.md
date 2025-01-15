# MSPR 2024 - 2025
<<<<<<< HEAD
### Cédric Sanchez - Valentin Fiess - Jason TCHAGA - Louis NECTOUX ###


------



Tutoriel : Configuration Docker + PyCharm avec JupyterLab
---

#### Étape 1 : Build et lancement du conteneur Docker

Build du conteneur Docker (en se positionnant dans le dossier) :

```bash
docker build -t python-data-env .
```

Lancer le conteneur Docker :
```bash
docker run --name python-data-env -p 8888:8888 -v $(pwd):/app -it python-data-env
```

Vérifier l’accès à JupyterLab :
Une fois le conteneur démarré, accédez à JupyterLab via http://127.0.0.1:8888/lab dans votre navigateur.

#### Étape 2 : Configuration dans PyCharm

Ajouter une configuration Docker dans PyCharm :
Allez dans File > Settings > Project > Python Interpreter.
Cliquez sur l’icône d’engrenage, puis sur Add Interpreter.
Sélectionnez Docker comme environnement.

Configurer l’interpréteur Docker :
Normalement tout est préconfigurer. Faites next, attendez que le build se fasse.
Validez les paramètres.

Configurer JupyterLab dans PyCharm :
Lancez PyCharm et ouvrez Settings > Jupyter.
Dans la section Jupyter Servers, ajoutez une nouvelle URL de serveur : http://127.0.0.1:8888/lab.
Validez la configuration.

---

Vérifier l’accès à JupyterLab :
Une fois le conteneur démarré, accédez à JupyterLab via http://127.0.0.1:8888/lab dans votre navigateur.