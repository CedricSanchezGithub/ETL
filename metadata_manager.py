#%% md
# # Gestion des métadonnées des espèces
# 
# Nous scannons les dossiers disponibles afin d'en faire un dataframe et réutiliser ces informations.
#  Puis nous récupérons les métadonnées depuis l'API Mistral grâce à un prompt optimisé (optimisation du grounding, du prompt engineering)
#  un sleep de 3s a été ajouté afin d'éviter de trop spam l'API
#%%
import pandas as pd
import os
from dotenv import load_dotenv
from mistralai import Mistral
import time

def create_metadata():
    #%%
    folder_all_animals = [d for d in os.listdir("ressource/image/train") if os.path.isdir(os.path.join("ressource/image/train", d))]
    df_all_animals = pd.DataFrame(folder_all_animals, columns=["Nom du dossier"])

    # Charger les variables d'environnement
    load_dotenv()

    # Nombre total d'animaux à scanner
    total_animaux = len(df_all_animals)
    reste_a_scanner = total_animaux

    api_key = os.environ.get("API_KEY")
    if not api_key:
        raise ValueError("La clé API n'est pas définie dans les variables d'environnement.")

    model = "open-mistral-nemo"

    client = Mistral(api_key=api_key)

    fichier_csv = "ressource/metadata.csv"

    # Supprimer le fichier s'il existe déjà
    if os.path.exists(fichier_csv):
        os.remove(fichier_csv)

    donnees_animaux = []

    for index, animal in enumerate(df_all_animals["Nom du dossier"]):

        reste_a_scanner = total_animaux - (index + 1)

        print(f"Il reste {reste_a_scanner} animaux à scanner")

        prompt = f"""
        En français, donne-moi les informations suivantes sur {animal} :
        - le nom de l'espèce (l'exacte nom que je t'ai donné)
        - le nom de l'espèce (traduit en français),
        - la famille,
        - le nom latin,
        - la population estimée (uniquement un nombre, sans texte, sans unité, sans ponctuation sauf le point ou la virgule pour les milliers),
        - la localisation (uniquement le ou les pays, séparés par un espace).
        - la description, une courte phrase décrivant l'animal.
    
        Attention :
        - Ne mets pas d'explication ou de phrase, uniquement les valeurs demandées.
        - Pour la population, écris uniquement un nombre sans texte. Par exemple : 1000000 au lieu de '1 million d'espèces environ'.
        - Pour la localisation, écris uniquement le ou les pays séparés par un espace.
        - Pour la Description, je souhaite 30 mots grand maximum.
        - Pour le nom de l'espèce en anglais, ce sera le nom que je t'aurai données lors du prompt, brut, tel quel, sans aucun changement. Notamment, sans majuscule.
        - Pour le nom en français, je souhaite éviter les mot composable ("Chat" au lieu de "Chat Domestique" par exemple)
    
        Présente les informations sous ce format exact :
        Espèce anglais : <nom de l'espèce en anglais>
        Espèce français : <nom de l'espèce traduit en français>
        Famille : <famille>
        Nom latin : <nom latin>
        Description: <description>
        Population estimée : <population estimée>
        Localisation : <localisation>
        """

        try:
            chat_response = client.chat.complete(
                model=model,
                messages=[{"role": "user", "content": prompt}]
            )

            # Extraire la réponse
            reponse = chat_response.choices[0].message.content
            print("Réponse reçue :", reponse)  # Ajouté pour le débogage

            # Parser la réponse pour extraire les valeurs
            informations = {}
            for ligne in reponse.split("\n"):
                if ":" in ligne:
                    cle, valeur = ligne.split(":", 1)
                    informations[cle.strip()] = valeur.strip()

            print("Informations extraites :", informations)  # Ajouté pour le débogage

            # Ajouter les informations à la liste
            donnees_animaux.append(informations)

        except Exception as e:
            print(f"Erreur lors de la récupération des infos pour {animal} : {e}")

        # Pause pour éviter d'être banni
        print("⏳ Attente de 3 secondes avant la prochaine requête...")
        time.sleep(3)

    # Création du DataFrame
    df_animaux = pd.DataFrame(donnees_animaux)


    # Sauvegarde dans un CSV
    df_animaux.to_csv(fichier_csv, index=False)

    print(f"Les informations des animaux ont été enregistrées dans {fichier_csv}.")
