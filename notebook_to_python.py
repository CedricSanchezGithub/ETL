# %%
import os
from functools import reduce

import albumentations as A
import cv2
import numpy as np
import pandas as pd
from PIL import Image
from pyspark.sql import DataFrame, Row, SparkSession
from pyspark.sql.functions import lit
from pyspark.sql.functions import rand, when, col


# Fonction pour récupérer les infos des images d'un dossier (en gérant les dossiers absents)
def get_image_info(folder_path):
    if not os.path.exists(folder_path):  # 📌 Vérifie si le dossier existe
        return 0, None, None  # ⚠️ Si absent → 0 images et tailles nulles

    image_files = [f for f in os.listdir(folder_path) if f.lower().endswith(('png', 'jpg', 'jpeg'))]
    num_images = len(image_files)

    if num_images == 0:
        return num_images, None, None  # Aucun fichier image

    widths, heights = [], []

    for img_file in image_files:
        img_path = os.path.join(folder_path, img_file)
        try:
            with Image.open(img_path) as img:
                widths.append(img.width)
                heights.append(img.height)
        except Exception as e:
            print(f"Erreur avec l'image {img_file}: {e}")

    avg_width = sum(widths) / len(widths) if widths else None
    avg_height = sum(heights) / len(heights) if heights else None

    return num_images, avg_width, avg_height


def main_function():
    # %%
    # Variables
    # Paramètres de connexion MySQL
    db_url = "jdbc:mysql://localhost:3306/wildlens?serverTimezone=UTC"
    db_properties = {"user": "root",
                     "password": "root",
                     "driver": "com.mysql.cj.jdbc.Driver"}
    mysql_driver_path = "installation/mysql-connector-j-9.1.0.jar"
    # %%
    # Initialisation de SparkSession
    spark = SparkSession.builder \
        .appName("WildLens ETL - MSPR 24-25") \
        .config("spark.jars", mysql_driver_path) \
        .getOrCreate()

    print("✅ Spark initialisé avec le driver MySQL :", mysql_driver_path)
    print("🔗 Driver chargé :", spark.sparkContext.getConf().get("spark.jars"))

    # %%
    try:
        df_tables = spark.read \
            .format("jdbc") \
            .option("url", db_url) \
            .option("dbtable", "information_schema.tables") \
            .option("user", "root") \
            .option("password", "root") \
            .option("driver", "com.mysql.cj.jdbc.Driver") \
            .load()

        df_tables.filter(df_tables["TABLE_SCHEMA"] == "wildlens").select("TABLE_NAME").show()

        print("✅ Connexion à MySQL réussie et tables listées avec succès !")

    except Exception as e:
        print(f"❌ Erreur de connexion à MySQL : {e}")

    # %%
    folder_all_animals = [d for d in os.listdir("ressource/image/train") if
                          os.path.isdir(os.path.join("ressource/image/train", d))]
    df_all_animals = pd.DataFrame(folder_all_animals, columns=["Nom du dossier"])

    # %%
    # Définition des chemins des datasets
    print("📂 Création du dataframe avec toutes les images...")
    image = "ressource/image/train"

    print("✅ Extraction des informations terminée.")

    print("🔄 Début de la Data Augmentation...")
    # Listes pour stocker les infos
    image_data = []

    # Parcourir chaque dossier et extraire les infos
    for folder in df_all_animals["Nom du dossier"]:
        # ✂️ Images recadrées - entraînement
        folder_path_train = os.path.join(image, folder)
        num_images_train, avg_width_train, avg_height_train = get_image_info(folder_path_train)
        image_data.append([folder, num_images_train, avg_width_train, avg_height_train])

    # Création des DataFrames
    df_image = pd.DataFrame(image_data,
                            columns=["Nom du dossier", "Nombre d'images", "Largeur Moyenne", "Hauteur Moyenne"])

    # %%
    # 📂 Définition du chemin des images
    image = "ressource/image/train"
    augmented_image_folder = "ressource/image/augmented_train"

    # 📝 Étape 1 : Calculer la médiane et Q3 du nombre d'images
    median_images = df_image["Nombre d'images"].median()
    q3_images = df_image["Nombre d'images"].quantile(0.75)

    print(f"Médiane: {median_images}, Q3: {q3_images}")
    print("✅ Data Augmentation terminée !")
    # %%
    # Création du dossier de sortie s'il n'existe pas
    os.makedirs(augmented_image_folder, exist_ok=True)

    # Calcul de la médiane et du Q3 pour équilibrer le dataset
    median_images = df_image["Nombre d'images"].median()
    q3_images = df_image["Nombre d'images"].quantile(0.75)

    # Détermination du coefficient de Data Augmentation
    df_image["Coeff"] = np.ceil(q3_images / df_image["Nombre d'images"])

    # Définition des transformations sans PyTorch
    augmentation = A.Compose([
        A.HorizontalFlip(p=0.5),
        A.RandomBrightnessContrast(p=0.2),
        A.Rotate(limit=30, p=0.5),
        A.GaussNoise(p=0.1),
        A.Resize(256, 256)  # Redimensionne sans ToTensorV2
    ])

    # Boucle sur chaque classe d'animaux
    for index, row in df_image.iterrows():
        if row["Coeff"] < 4:
            folder_name = row["Nom du dossier"]
            coeff = int(row["Coeff"])

            original_folder = os.path.join(image, folder_name)
            augmented_folder = os.path.join(augmented_image_folder, folder_name)
            os.makedirs(augmented_folder, exist_ok=True)

            image_files = [f for f in os.listdir(original_folder) if f.lower().endswith(('png', 'jpg', 'jpeg'))]

            for img_file in image_files:
                img_path = os.path.join(original_folder, img_file)
                img = cv2.imread(img_path)  # Lecture avec OpenCV (BGR)

                if img is None:
                    print(f"❌ Erreur de lecture de l'image {img_file}")
                    continue

                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  # Conversion en RGB (évite les problèmes de couleur)

                for i in range(coeff):  # Générer plusieurs images augmentées
                    augmented = augmentation(image=img)["image"]
                    new_img_path = os.path.join(augmented_folder, f"aug_{i}_{img_file}")
                    cv2.imwrite(new_img_path, cv2.cvtColor(augmented, cv2.COLOR_RGB2BGR))  # Sauvegarde avec OpenCV

    print("✅ Data Augmentation terminée avec succès !")
    print("🔄 Fusion des données avec les métadonnées...")
    # %%
    # Listes pour stocker les infos
    image_data_new = []
    image_new = "ressource/image/augmented_train"

    # Parcourir chaque dossier et extraire les infos
    for folder in df_all_animals["Nom du dossier"]:
        # ✂️ Images recadrées - entraînement
        folder_path_train = os.path.join(image_new, folder)
        num_images_train, avg_width_train, avg_height_train = get_image_info(folder_path_train)
        image_data_new.append([folder, num_images_train, avg_width_train, avg_height_train])

    # Création des DataFrames
    image_data_new = pd.DataFrame(image_data_new,
                                  columns=["Nom du dossier", "Nombre d'images", "Largeur Moyenne", "Hauteur Moyenne"])
    # %% md
    # ## Labélisation
    # Le dataframe d'images et les métadata sont fusionnées afin que chaque image corresponde à des métadonnées : c'est la labélisation.
    # %%
    df_metadata = pd.read_csv("./ressource/metadata.csv")

    df_merged = pd.merge(image_data_new, df_metadata, left_on='Nom du dossier', right_on='Espèce anglais', how='left')

    print(df_merged)
    print(df_merged.shape)
    print(df_merged.head(10))

    df_merged.to_csv("./ressource/data_merged.csv", header=True)

    if print(df_merged['Espèce anglais'].isna().sum()):
        print("Toutes les lignes ont trouvés une correspondance")
    print("✅ Fusion des datasets terminée !")
    # %%
    print("📊 Création des partitions de données pour Spark...")
    df_merged_spark = spark.createDataFrame(df_merged)
    image_new = "ressource/image/augmented_train"

    df_dict = {}
    for dossier in df_merged_spark.select("Nom du dossier").distinct().rdd.flatMap(lambda x: x).collect():
        folder_path = os.path.join(image_new, dossier)
        if os.path.exists(folder_path):
            df_images = spark.createDataFrame(
                [(dossier, os.path.join(dossier, img)) for img in os.listdir(folder_path)],
                ["Nom du dossier", "Chemin Relatif"])
            df_dict[dossier] = df_images.join(df_merged_spark, on="Nom du dossier", how="left")

    for dossier, df in df_dict.items():
        df.write.mode("overwrite").parquet(f"ressource/dataframes_parquet/{dossier}")
        df.write.mode("overwrite").csv(f"ressource/dataframes_csv/{dossier}")

    train_ratio = 0.8
    val_ratio = 0.1

    for dossier, df in df_dict.items():
        df = df.withColumn("rand_val", rand())

        df = df.withColumn(
            "state",
            when(col("rand_val") <= train_ratio, 1)
            .when(col("rand_val") <= (train_ratio + val_ratio), 2)
            .otherwise(3)
        )

        df_dict[dossier] = df

        df.write.mode("overwrite").parquet(f"ressource/dataframes_parquet/{dossier}")
        df.write.mode("overwrite").csv(f"ressource/dataframes_csv/{dossier}")

        print(f"��� State ajouté et fichier enregistré pour {dossier}")

    if df_dict:
        df_final = reduce(DataFrame.unionAll, df_dict.values())
        print(f" Fusion complète ! Le DataFrame final contient {df_final.count()} images.")
        df_final.write.mode("overwrite").parquet("ressource/dataframes_parquet/all_images")
        df_final.coalesce(1).write.mode("overwrite").csv("ressource/dataframes_csv/all_images", header=True)
    else:
        print("⚠️ Aucun DataFrame à fusionner !")
    print("✅ Partitionnement terminé.")
    print("🔄 Mise à jour des tables MySQL...")
    # %%
    print("Colonnes de df_facts :", df_final.columns)
    print(df_final.describe())
    # %%
    df_existing = spark.read.jdbc(url=db_url, table="wildlens_etat", properties=db_properties)

    if df_existing.count() == 0:
        print("La table wildlens_etat est vide, insertion des données...")

        df_etat = spark.createDataFrame([
            Row(id_etat=1, type="train"),
            Row(id_etat=2, type="validation"),
            Row(id_etat=3, type="test")
        ])

        df_etat.write.mode("append").jdbc(url=db_url, table="wildlens_etat", properties=db_properties)
    # %%
    df_existing = spark.read.jdbc(url=db_url, table="wildlens_facts", properties=db_properties)

    if df_existing.count() == 0:
        print("La table wildlens_facts est vide, insertion des données...")

        df_facts = df_final.select(
            "Espèce français", "Famille", "Nom latin", "Description", "Population estimée", "Localisation",
            "Espèce anglais",
            "Nombre d'images"
        ).dropDuplicates()

        df_facts = (df_facts.withColumnRenamed("Espèce anglais", "nom_en")
                    .withColumnRenamed("Population estimée", "population_estimee")
                    .withColumnRenamed("Nombre d'images", "nombre_image")
                    .withColumnRenamed("Espèce français", "nom_fr")
                    .withColumnRenamed("Nom latin", "nom_latin"))

        df_facts = df_facts.withColumn("coeff_multiplication", lit(1))

        df_facts.write.jdbc(url=db_url, table="wildlens_facts", mode="append", properties=db_properties)

        print("✅ Table wildlens_facts mise à jour avec succès !")

    # %%
    df_existing = spark.read.jdbc(url=db_url, table="wildlens_images", properties=db_properties)

    if df_existing.count() == 0:
        print("La table wildlens_images est vide, insertion des données...")

        df_images = spark.read.jdbc(url=db_url, table="wildlens_facts", properties=db_properties)
        df_id_espece = df_images.select("id_espece", "nom_fr").distinct()

        if "id_espece" in df_final.columns:
            df_final = df_final.drop("id_espece")

        # Effectuer la jointure pour récupérer l'ID de l'espèce
        df_final = df_final.join(df_id_espece, df_final["Espèce français"] == df_id_espece["nom_fr"], "left")

        # Supprimer la colonne "nom_fr" après la jointure (elle ne sert plus)
        df_final = df_final.drop("nom_fr")
        print(df_final.show())

        df_facts = (df_facts.withColumnRenamed("Chemin Relatif", "image")
                    .withColumnRenamed("id_espece", "id_espece")
                    .withColumnRenamed("state", "id_etat"))

        df_facts.write.jdbc(url=db_url, table="wildlens_images", mode="append", properties=db_properties)

        print("✅ Table wildlens_images mise à jour avec succès !")

    print("🎉 Script terminé avec succès !")

    # Fermeture propre de Spark
    spark.stop()
    print("🛑 SparkSession fermée.")