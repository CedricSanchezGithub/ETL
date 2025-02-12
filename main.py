import os
import sys

from dotenv import load_dotenv
from mistralai import Mistral

load_dotenv()

api_key = os.environ.get("API_KEY")
if not api_key:
    raise ValueError("La clé API n'est pas définie dans les variables d'environnement.")

model = "open-mistral-nemo"

client = Mistral(api_key=api_key)

# Récupérer le nom de l'animal depuis les arguments de ligne de commande
if len(sys.argv) < 2:
    raise ValueError("Veuillez fournir le nom de l'animal en argument de ligne de commande.")
animal = sys.argv[1]

prompt = f"""
En français, donne-moi les informations suivantes sur {animal} :
- le nom de l'espèce,
- la famille,
- le nom latin,
- la population estimée (uniquement un nombre, sans texte, sans unité, sans ponctuation sauf le point ou la virgule pour les milliers),
- la localisation (uniquement le ou les pays, séparés par un espace).
- la description, une courte phrase décrivant l'animale. 

Attention :
- Ne mets pas d'explication ou de phrase, uniquement les valeurs demandées.
- Pour la population, écris uniquement un nombre sans texte. Par exemple : 1000000 au lieu de '1 million d'espèces environ'.
- Pour la localisation, écris uniquement le ou les pays séparés par un espace.
- Pour la Description, je souhaite 30 mots grand maximum.

Présente les informations sous ce format exact :
Espèce : <nom de l'espèce>
Famille : <famille>
Nom latin : <nom latin>
Description: <description>
Population estimée : <population estimée>
Localisation : <localisation>
"""

chat_response = client.chat.complete(
    model=model,
    messages=[{"role": "user", "content": prompt}]
)

print(chat_response.choices[0].message.content)