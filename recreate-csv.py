# import csv
# import subprocess
#
# input_csv_path = 'data/csv/infos_especes.csv'
# output_csv_path = 'data/csv/nouvelles_infos_especes.csv'
#
# # Lire le fichier CSV d'entrée et extraire la colonne 'Espèce'
# with open(input_csv_path, mode='r', encoding='utf-8-sig') as infile:
#     reader = csv.DictReader(infile, delimiter=';')
#     print("Noms de colonnes lus :", reader.fieldnames)
#     especes = [row['Espèce'] for row in reader if 'Espèce' in row]
#
# # Créer le fichier CSV de sortie avec les nouvelles colonnes
# with open(output_csv_path, mode='w', newline='', encoding='utf-8') as outfile:
#     fieldnames = ['Nom', 'Famille', 'Nom latin', 'Description', 'Population estimée', 'Localisation']
#     writer = csv.DictWriter(outfile, fieldnames=fieldnames)
#     writer.writeheader()
#
#     # Pour chaque espèce, appeler le script main.py et écrire les nouvelles données dans le fichier CSV de sortie
#     for espece in especes:
#         print(f"Traitement de l'espèce : {espece}")
#         result = subprocess.run(['python3', 'main.py', espece], capture_output=True, text=True)
#         if result.returncode == 0:
#             # Parse the output from main.py
#             lines = result.stdout.strip().split('\n')
#             print(f"Sortie de main.py pour {espece} : {lines}")
#             if len(lines) == len(fieldnames):
#                 data = {field: line.split(': ')[1] for field, line in zip(fieldnames, lines)}
#                 writer.writerow(data)
#             else:
#                 print(
#                     f"Erreur : Le nombre de lignes de sortie ne correspond pas au nombre de champs attendus pour l'espèce {espece}.")
#         else:
#             print(f"Erreur lors de l'exécution du script pour l'espèce {espece}: {result.stderr}")