# %% md
# # Gestion des métadonnées des espèces
#
# Nous scannons les dossiers disponibles afin d'en faire un dataframe et réutiliser ces informations.
# Puis nous récupérons les métadonnées depuis l'API Mistral et Gemini, comparons leurs résultats pour réduire les erreurs potentielles, et créons un CSV final optimisé.
# Un sleep de 3s a été ajouté afin d'éviter de trop spam les APIs.
# %%
import json
import os
import random
import time
from datetime import datetime

import pandas as pd
from dotenv import load_dotenv
from google import genai
from mistralai import Mistral

skip_test = not os.path.exists("ressource/image/train")

def metadata_manager():
    # Scanner les dossiers d'animaux
    folder_all_animals = [
        d
        for d in os.listdir("ressource/image/train")
        if os.path.isdir(os.path.join("ressource/image/train", d))
    ]
    df_all_animals = pd.DataFrame(folder_all_animals, columns=["Nom du dossier"])

    # Charger les variables d'environnement
    load_dotenv()

    # Nombre total d'animaux à scanner
    total_animaux = len(df_all_animals)
    reste_a_scanner = total_animaux
    # %%
    # Récupération des clés API
    mistral_api_key = os.environ.get("mistral_api_key")
    if not mistral_api_key:
        raise ValueError(
            "La clé API Mistral n'est pas définie dans les variables d'environnement."
        )

    gemini_api_key = os.environ.get("gemini_api_key")
    if not gemini_api_key:
        raise ValueError(
            "La clé API gemini n'est pas définie dans les variables d'environnement."
        )

    # Configuration des modèles
    mistral_model = "open-mistral-nemo"
    gemini_model = "gemini-2.0-flash"

    # Initialisation des clients
    mistral_client = Mistral(api_key=mistral_api_key)
    gemini_client = genai.Client(api_key=gemini_api_key)
    # %%
    # Chemins des fichiers CSV
    fichier_csv_mistral = "ressource/metadata_mistral.csv"
    fichier_csv_gemini = "ressource/metadata_gemini.csv"
    fichier_csv_comparaison = "ressource/metadata_comparaison.csv"
    fichier_csv_final = "ressource/metadata_final.csv"

    # Supprimer les fichiers s'ils existent déjà
    for fichier in [
        fichier_csv_mistral,
        fichier_csv_gemini,
        fichier_csv_comparaison,
        fichier_csv_final,
    ]:
        if os.path.exists(fichier):
            os.remove(fichier)

    # Initialisation des listes pour stocker les données
    donnees_animaux_mistral = []
    donnees_animaux_gemini = []
    donnees_animaux_final = []
    comparaisons = []

    # %%
    # Fonction améliorée pour faire un appel à l'API avec gestion de toutes les erreurs
    def make_api_call_with_retry(
        client, model, messages, max_retries=5, initial_delay=5
    ):
        for attempt in range(max_retries):
            try:
                # Ajouter un délai exponentiel avec un peu d'aléatoire
                if attempt > 0:
                    # Délai plus long pour les tentatives supplémentaires
                    delay = initial_delay * (2**attempt) + random.uniform(0, 2)
                    print(
                        f"⏳ Tentative {attempt + 1}/{max_retries} - Attente de {delay:.1f} secondes..."
                    )
                    time.sleep(delay)

                # Timestamp pour le log
                timestamp = datetime.now().strftime("%H:%M:%S")
                print(f"[{timestamp}] Appel API - Tentative {attempt + 1}")

                # Faire l'appel à l'API
                response = client.chat.complete(model=model, messages=messages)
                return response
            except Exception as e:
                # Gérer tous les types d'erreurs, pas seulement 429
                error_type = "Rate limit" if "429" in str(e) else "API"
                print(
                    f"⚠️ {error_type} erreur (tentative {attempt + 1}/{max_retries}): {e}"
                )

                # Si c'est la dernière tentative, lever l'exception
                if attempt == max_retries - 1:
                    raise e

                # Sinon continuer avec la prochaine tentative après le délai

        # Ce code ne devrait jamais être atteint car on lève l'exception à la dernière tentative
        raise Exception(f"Échec après {max_retries} tentatives")

    # %%
    # Fonction pour faire un appel à l'API Gemini avec retry
    def make_gemini_call_with_retry(
        client, model, prompt, max_retries=5, initial_delay=5
    ):
        for attempt in range(max_retries):
            try:
                # Ajouter un délai exponentiel si ce n'est pas la première tentative
                if attempt > 0:
                    delay = initial_delay * (2**attempt) + random.uniform(0, 2)
                    print(
                        f"⏳ Tentative Gemini {attempt + 1}/{max_retries} - Attente de {delay:.1f} secondes..."
                    )
                    time.sleep(delay)

                # Timestamp pour le log
                timestamp = datetime.now().strftime("%H:%M:%S")
                print(f"[{timestamp}] Appel API Gemini - Tentative {attempt + 1}")

                # Faire l'appel à l'API Gemini
                response = client.models.generate_content(model=model, contents=prompt)
                return response
            except Exception as e:
                error_type = "Indisponibilité" if "503" in str(e) else "API"
                print(
                    f"⚠️ Gemini {error_type} erreur (tentative {attempt + 1}/{max_retries}): {e}"
                )

                # Si c'est la dernière tentative, lever l'exception
                if attempt == max_retries - 1:
                    raise e

        # Ce code ne devrait jamais être atteint
        raise Exception(f"Échec après {max_retries} tentatives avec Gemini")

    # %%
    folder_all_animals = [
        d
        for d in os.listdir("ressource/image/train")
        if os.path.isdir(os.path.join("ressource/image/train", d))
    ]
    df_all_animals = pd.DataFrame(folder_all_animals, columns=["Nom du dossier"])

    # Nombre total d'animaux à scanner
    total_animaux = len(df_all_animals)

    # %%
    def get_animal_info(animal):
        prompt = f"""
                En français, donne-moi les informations suivantes sur {animal} :
                - le nom de l'espèce (l'exacte nom que je t'ai donné)
                - le nom de l'espèce (traduit en français),
                - la famille,
                - le nom latin,
                - la population estimée (uniquement un nombre, sans texte, sans unité, sans ponctuation, sans espace entre les nombre, sans approximation, incertitude,  inconnue ou 0),
                - la localisation (uniquement le ou les pays, séparés par un espace).
                - la description, une courte phrase décrivant l'animal.

                Attention :
                - Ne mets pas d'explication ou de phrase, uniquement les valeurs demandées.
                - Pour la population, écris uniquement un nombre sans texte. Par exemple : 1000000 au lieu de '1 million d'espèces environ' ou '1 000 000'.
                - Pour la localisation, écris uniquement le ou les pays séparés par un espace.
                - Pour la Description, je souhaite 30 mots grand maximum.
                - Pour le nom de l'espèce en anglais, ce sera le nom que je t'aurai données lors du prompt, brut, tel quel, sans aucun changement. Notamment, sans majuscule.
                - Pour le nom en français, je souhaite éviter les mot composable ("Chat" au lieu de "Chat Domestique" par exemple)
                - Pour la population estimé, je souhaite forcément un double, pas un entier. Par exemple, 1000000.0 au lieu de 1000000 ou 1.0 million.
                
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
            # Réponse avec Mistral
            chat_response_mistral = make_api_call_with_retry(
                client=mistral_client,
                model=mistral_model,
                messages=[{"role": "user", "content": prompt}],
            )
            reponse_mistral = chat_response_mistral.choices[0].message.content
            print("Réponse Mistral reçue")

            # Délai entre les deux modèles
            time.sleep(2)

            # Réponse avec Gemini
            response = make_gemini_call_with_retry(
                client=gemini_client, model=gemini_model, prompt=prompt
            )
            reponse_gemini = response.text
            print("Réponse Gemini reçue")

            # Parser les réponses
            informations_mistral = {}
            for ligne in reponse_mistral.split("\n"):
                if ":" in ligne:
                    cle, valeur = ligne.split(":", 1)
                    informations_mistral[cle.strip()] = valeur.strip()

            informations_gemini = {}
            for ligne in reponse_gemini.split("\n"):
                if ":" in ligne:
                    cle, valeur = ligne.split(":", 1)
                    informations_gemini[cle.strip()] = valeur.strip()

            return informations_mistral, informations_gemini

        except Exception as e:
            print(f"Erreur lors de la récupération des infos pour {animal} : {e}")
            return None, None

    # %%
    def compare_results(animal, informations_mistral, informations_gemini):
        try:
            prompt_comparaison = f"""
                    Analyse ces deux ensembles de métadonnées pour l'animal "{animal}":

                    Métadonnées de Mistral:
                    {json.dumps(informations_mistral, indent=2, ensure_ascii=False)}

                    Métadonnées de Gemini:
                    {json.dumps(informations_gemini, indent=2, ensure_ascii=False)}

                    Objectif: Identifier les différences importantes pour créer un CSV final fiable en combinant les meilleures réponses.

                    Pour chaque champ où tu observes une différence significative (sémantique ou orthographique):
                    1. Identifie précisément le champ concerné
                    2. Compare objectivement les deux valeurs
                    3. Détermine laquelle est la plus précise/correcte avec justification courte
                    4. Indique "ERREUR" si les deux valeurs semblent incorrectes ou contradictoires

                    Format de réponse:
                    - Structure ta réponse sous forme de liste par champ
                    - Pour chaque champ avec différence, indique clairement le champ, la valeur à retenir et pourquoi
                    - Si aucune différence significative n'est trouvée, indique "Aucune différence significative"
                    - Si une valeur est manifestement incorrecte, signale-la avec "ERREUR: [explication]"

                    Fournis également un ensemble de métadonnées final qui combine le meilleur des deux sources.
                    Présente ces métadonnées finales sous le même format que les entrées originales:
                    Espèce anglais : <valeur>
                    Espèce français : <valeur>
                    Famille : <valeur>
                    Nom latin : <valeur>
                    Description: <valeur>
                    Population estimée : <valeur>
                    Localisation : <valeur>
                    """
            # Délai avant l'appel de comparaison pour éviter le rate limiting
            print("⏳ Attente avant comparaison pour éviter le rate limiting...")
            time.sleep(3)

            comparaison_response = make_api_call_with_retry(
                client=mistral_client,
                model=mistral_model,
                messages=[{"role": "user", "content": prompt_comparaison}],
            )
            reponse_comparaison = comparaison_response.choices[0].message.content

            # Extraire les métadonnées finales de la réponse
            informations_final = {}
            section_finale_trouvee = False
            lignes_finales = []

            for ligne in reponse_comparaison.split("\n"):
                if "Espèce anglais :" in ligne and not section_finale_trouvee:
                    section_finale_trouvee = True

                if section_finale_trouvee and ":" in ligne:
                    lignes_finales.append(ligne)

            # Si des métadonnées finales ont été trouvées, les utiliser
            if lignes_finales:
                for ligne in lignes_finales:
                    if ":" in ligne:
                        cle, valeur = ligne.split(":", 1)
                        if cle.strip() != "ERREUR":  # Ignorer les champs ERREUR
                            informations_final[cle.strip()] = valeur.strip()
            else:
                # Si pas de section finale, utiliser les métadonnées de Mistral par défaut
                informations_final = {
                    k: v
                    for k, v in informations_mistral.copy().items()
                    if k != "ERREUR"
                }

            # Vérifier que toutes les colonnes requises sont présentes
            colonnes_requises = [
                "Espèce anglais",
                "Espèce français",
                "Famille",
                "Nom latin",
                "Description",
                "Population estimée",
                "Localisation",
            ]

            for colonne in colonnes_requises:
                if (
                    colonne not in informations_final
                    or not informations_final[colonne]
                    or informations_final[colonne].upper() == "ERREUR"
                ):
                    # Au lieu d'indiquer ERREUR, utiliser une valeur par défaut significative
                    if colonne == "Espèce anglais":
                        informations_final[colonne] = animal
                    elif colonne == "Population estimée":
                        informations_final[colonne] = "0"  # Valeur numérique par défaut
                    else:
                        informations_final[colonne] = (
                            f"Information non disponible pour {animal}"
                        )

            return reponse_comparaison, informations_final

        except Exception as e:
            print(f"Erreur lors de la comparaison pour {animal}: {e}")
            # Créer un dictionnaire sans la clé ERREUR
            informations_final = {
                k: v for k, v in informations_mistral.copy().items() if k != "ERREUR"
            }

            # Garantir que toutes les colonnes requises sont présentes
            colonnes_requises = [
                "Espèce anglais",
                "Espèce français",
                "Famille",
                "Nom latin",
                "Description",
                "Population estimée",
                "Localisation",
            ]

            for colonne in colonnes_requises:
                if colonne not in informations_final or not informations_final[colonne]:
                    if colonne == "Espèce anglais":
                        informations_final[colonne] = animal
                    elif colonne == "Population estimée":
                        informations_final[colonne] = "0"
                    else:
                        informations_final[colonne] = (
                            f"Information non disponible pour {animal}"
                        )

            return f"Erreur: {str(e)}", informations_final

    # %%
    # Traitement des animaux
    for index, animal in enumerate(df_all_animals["Nom du dossier"]):
        reste_a_scanner = total_animaux - (index + 1)
        print(
            f"Animal en cours: {animal} - Il reste {reste_a_scanner} animaux à scanner"
        )

        try:
            # Sauvegarde intermédiaire tous les 5 animaux ou à la fin
            if index % 5 == 0 or index == total_animaux - 1:
                # Sauvegarde intermédiaire
                print(
                    f"💾 Sauvegarde intermédiaire des données (animal {index + 1}/{total_animaux})..."
                )
                pd.DataFrame(donnees_animaux_final).to_csv(
                    "ressource/metadata_final_intermediate.csv", index=False
                )

            # Reste du code de traitement
            informations_mistral, informations_gemini = get_animal_info(animal)

            if informations_mistral and informations_gemini:
                # Ajouter à nos listesgemini_client
                donnees_animaux_mistral.append(informations_mistral)
                donnees_animaux_gemini.append(informations_gemini)

                # Créer une entrée pour la comparaison
                comparaison = {"Espèce": animal, "Différences": []}

                # Comparer les résultats
                reponse_comparaison, informations_final = compare_results(
                    animal, informations_mistral, informations_gemini
                )
                comparaison["Différences"] = reponse_comparaison
                comparaisons.append(comparaison)
                donnees_animaux_final.append(informations_final)
            else:
                # En cas d'erreur générale, ajouter une entrée d'erreur aux données finales
                informations_final = {
                    "Espèce anglais": animal,
                    "Espèce français": f"Information non disponible pour {animal}",
                    "Famille": f"Information non disponible pour {animal}",
                    "Nom latin": f"Information non disponible pour {animal}",
                    "Description": f"Information non disponible pour {animal}",
                    "Population estimée": "0",
                    "Localisation": f"Information non disponible pour {animal}",
                }
                donnees_animaux_final.append(informations_final)

        except Exception as e:
            print(f"🔴 Erreur majeure lors du traitement de {animal}: {e}")
            print("Sauvegarde d'urgence et passage à l'animal suivant...")

            # Ajouter une entrée d'erreur
            informations_final = {
                "Espèce anglais": animal,
                "Espèce français": f"Erreur de traitement - {str(e)[:50]}",
                "Famille": f"Information non disponible pour {animal}",
                "Nom latin": f"Information non disponible pour {animal}",
                "Description": "Erreur lors du traitement de cet animal",
                "Population estimée": "0",
                "Localisation": f"Information non disponible pour {animal}",
            }
            donnees_animaux_final.append(informations_final)

            # Sauvegarde d'urgence
            pd.DataFrame(donnees_animaux_final).to_csv(
                "ressource/metadata_final_emergency.csv", index=False
            )

            # Pause plus longue après une erreur
            print("⏳ Attente de 5 secondes après erreur...")
            time.sleep(5)
            continue

        # Pause pour éviter d'être banni
        print("⏳ Attente de 3 secondes avant la prochaine requête...")
        time.sleep(3)  # Nettoyage final des données avant création du DataFrame
    # Nettoyage final des données avant création du DataFrame
    colonnes_a_conserver = [
        "Espèce anglais",
        "Espèce français",
        "Famille",
        "Nom latin",
        "Description",
        "Population estimée",
        "Localisation",
    ]

    # Fonction pour fusionner les informations des colonnes normales et étoilées
    def fusionner_donnees(row, animal):
        resultat = {}
        colonnes_a_conserver = [
            "Espèce anglais",
            "Espèce français",
            "Famille",
            "Nom latin",
            "Description",
            "Population estimée",
            "Localisation",
        ]

        for col in colonnes_a_conserver:
            # Initialiser la colonne avec une valeur par défaut
            resultat[col] = f"Information non disponible pour {animal}"

            # Récupérer les valeurs normales et avec astérisques
            valeur = row.get(col, "")
            valeur_etoile = row.get(f"* {col}", "")

            # Prioriser la valeur non vide et différente de "Information non disponible"
            if valeur and "Information non disponible" not in str(valeur):
                resultat[col] = valeur
            elif valeur_etoile and "Information non disponible" not in str(
                valeur_etoile
            ):
                resultat[col] = valeur_etoile
            elif valeur:
                resultat[col] = valeur
            elif valeur_etoile:
                resultat[col] = valeur_etoile

            # Gestion spécifique de la population estimée
            if col == "Population estimée":
                # Si après toutes les vérifications, la valeur est toujours la valeur par défaut, mettre "0"
                if resultat[col] == f"Information non disponible pour {animal}":
                    resultat[col] = "0"
                else:
                    # Supprimer les espaces et caractères non numériques
                    resultat[col] = "".join(filter(str.isdigit, str(resultat[col])))
                    if not resultat[col]:
                        resultat[col] = "0"

        return resultat

    # Traiter chaque animal pour récupérer les meilleures données
    donnees_animaux_final_fusionnees = []
    for donnee in donnees_animaux_final:
        animal = donnee.get("Espèce anglais", "animal inconnu")
        donnee_fusionnee = fusionner_donnees(donnee, animal)
        donnees_animaux_final_fusionnees.append(donnee_fusionnee)

    # Création du DataFrame final avec uniquement les colonnes souhaitées
    df_animaux_final = pd.DataFrame(donnees_animaux_final_fusionnees)
    df_animaux_final = df_animaux_final[
        colonnes_a_conserver
    ]  # Garantir l'ordre des colonnes

    # Pour s'assurer qu'il n'y a pas de colonnes avec astérisques dans le DataFrame final
    colonnes_filtrees = [
        col for col in df_animaux_final.columns if not col.startswith("*")
    ]
    df_animaux_final = df_animaux_final[colonnes_filtrees]

    # Supprimer le fichier s'il existe déjà pour éviter l'ajout de colonnes
    if os.path.exists(fichier_csv_final):
        os.remove(fichier_csv_final)

    # Sauvegarde du CSV final (avec mode='w' pour s'assurer de réécrire le fichier)
    df_animaux_final["Population estimée"] = pd.to_numeric(df_animaux_final["Population estimée"],
                                                           errors="coerce").fillna(0)
    df_animaux_final.to_csv(fichier_csv_final, index=False, mode="w")
    print(f"✅ Fichier final créé avec succès : {fichier_csv_final}")
    # %%
    # Supprimer les fichiers intermédiaires
    fichiers_intermediaires = [
        "ressource/metadata_final_intermediate.csv",
        "ressource/metadata_final_emergency.csv",
    ]
    for fichier in fichiers_intermediaires:
        if os.path.exists(fichier):
            try:
                os.remove(fichier)
                print(f"✅ Fichier intermédiaire supprimé : {fichier}")
            except Exception as e:
                print(f"⚠️ Impossible de supprimer {fichier}: {e}")
    # %%
    # Création des DataFrames
    df_animaux_mistral = pd.DataFrame(donnees_animaux_mistral)
    df_animaux_gemini = pd.DataFrame(donnees_animaux_gemini)
    df_comparaisons = pd.DataFrame(comparaisons)
    df_animaux_final = pd.DataFrame(donnees_animaux_final)

    # Affichage des résultats
    print("Résultats Mistral:")
    print(df_animaux_mistral)

    print("Résultats Gemini:")
    print(df_animaux_gemini)

    print("Comparaison des résultats:")
    print(df_comparaisons)

    print("Résultats finaux optimisés:")
    print(df_animaux_final)

    # Sauvegarde dans des CSV
    df_animaux_mistral.to_csv(fichier_csv_mistral, index=False)
    df_animaux_gemini.to_csv(fichier_csv_gemini, index=False)
    df_comparaisons.to_csv(fichier_csv_comparaison, index=False)
    df_animaux_final.to_csv(fichier_csv_final, index=False)

    print("Les résultats ont été enregistrés dans les fichiers suivants:")
    print(f" - {fichier_csv_mistral}")
    print(f" - {fichier_csv_gemini}")
    print(f" - {fichier_csv_comparaison}")
    print(f" - {fichier_csv_final}")

if __name__ == "__main__" :
    metadata_manager()
