import os
import sys

from dotenv import load_dotenv
from mistralai import Mistral

load_dotenv()

api_key = os.environ.get("api_key")
if not api_key:
    raise ValueError("La clé API n'est pas définie dans les variables d'environnement.")

model = "open-mistral-nemo"

client = Mistral(api_key=api_key)

# Récupérer le nom de l'animal depuis les arguments de ligne de commande
if len(sys.argv) < 2:
    raise ValueError("Veuillez fournir le nom de l'animal en argument de ligne de commande.")
animal = sys.argv[1]

chat_response = client.chat.complete(
    model=model,
    messages=[
        {
            "role": "user",
            "content": f"En français, donne-moi les informations suivantes sur {animal} : le nom de l'espèce, la famille, le nom latin, description (courte description de l'animal), la population estimée (uniquement le nombre), la plus grande menace (texte court), la localisation, et le slogan (texte court). Présente les informations au format : Espèce : <nom de l'espèce>\nFamille : <famille>\nNom latin : <nom latin>\nPopulation estimée : <population estimée>\nPlus grande menace : <plus grande menace>\nLocalisation : <localisation>\nSlogan : <slogan>"
        },
    ]
)
print(chat_response.choices[0].message.content)