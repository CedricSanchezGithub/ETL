# %%
import os
from functools import reduce

import albumentations as A
import cv2
import numpy as np
import pandas as pd
from PIL import Image
from pyspark.sql import DataFrame, Row, SparkSession
from pyspark.sql.functions import lit, rand, when, col

# 📌 Définition des chemins de base
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TRAIN_IMAGE_DIR = os.path.join(BASE_DIR, "ressource", "image", "train")
AUGMENTED_IMAGE_DIR = os.path.join(BASE_DIR, "ressource", "image", "augmented_train")
METADATA_CSV_PATH = os.path.join(BASE_DIR, "ressource", "metadata.csv")
MERGED_CSV_PATH = os.path.join(BASE_DIR, "ressource", "data_merged.csv")
PARQUET_OUTPUT_DIR = os.path.join(BASE_DIR, "ressource", "dataframes_parquet")
CSV_OUTPUT_DIR = os.path.join(BASE_DIR, "ressource", "dataframes_csv")
MYSQL_DRIVER_PATH = os.path.join(BASE_DIR, "installation", "mysql-connector-j-9.1.0.jar")

# 📂 Fonction d'extraction d'infos sur les images
def get_image_info(folder_path):
    if not os.path.exists(folder_path):
        return 0, None, None

    image_files = [f for f in os.listdir(folder_path) if f.lower().endswith(('png', 'jpg', 'jpeg'))]
    num_images = len(image_files)

    if num_images == 0:
        return num_images, None, None

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

# ✅ Point d'entrée principal
def main_function():
    # Paramètres de connexion MySQL
    db_url = "jdbc:mysql://localhost:3306/wildlens?serverTimezone=UTC"
    db_properties = {"user": "root", "password": "root", "driver": "com.mysql.cj.jdbc.Driver"}
    mysql_driver_path = MYSQL_DRIVER_PATH

    # Initialisation de Spark
    spark = SparkSession.builder \
        .appName("WildLens ETL - MSPR 24-25") \
        .config("spark.jars", mysql_driver_path) \
        .getOrCreate()

    print("✅ Spark initialisé avec le driver MySQL :", mysql_driver_path)

    # Vérification MySQL
    try:
        df_tables = spark.read.format("jdbc") \
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

    folder_all_animals = [d for d in os.listdir(TRAIN_IMAGE_DIR) if
                          os.path.isdir(os.path.join(TRAIN_IMAGE_DIR, d))]
    df_all_animals = pd.DataFrame(folder_all_animals, columns=["Nom du dossier"])

    print("📂 Création du dataframe avec toutes les images...")

    image_data = []
    for folder in df_all_animals["Nom du dossier"]:
        folder_path_train = os.path.join(TRAIN_IMAGE_DIR, folder)
        num_images_train, avg_width_train, avg_height_train = get_image_info(folder_path_train)
        image_data.append([folder, num_images_train, avg_width_train, avg_height_train])

    df_image = pd.DataFrame(image_data,
                            columns=["Nom du dossier", "Nombre d'images", "Largeur Moyenne", "Hauteur Moyenne"])

    median_images = df_image["Nombre d'images"].median()
    q3_images = df_image["Nombre d'images"].quantile(0.75)

    print(f"Médiane: {median_images}, Q3: {q3_images}")
    print("✅ Extraction des informations terminée.")

    os.makedirs(AUGMENTED_IMAGE_DIR, exist_ok=True)
    df_image["Coeff"] = np.ceil(q3_images / df_image["Nombre d'images"])

    augmentation = A.Compose([
        A.HorizontalFlip(p=0.5),
        A.RandomBrightnessContrast(p=0.2),
        A.Rotate(limit=30, p=0.5),
        A.GaussNoise(p=0.1),
        A.Resize(256, 256)
    ])

    for index, row in df_image.iterrows():
        if row["Coeff"] < 4:
            folder_name = row["Nom du dossier"]
            coeff = int(row["Coeff"])

            original_folder = os.path.join(TRAIN_IMAGE_DIR, folder_name)
            augmented_folder = os.path.join(AUGMENTED_IMAGE_DIR, folder_name)
            os.makedirs(augmented_folder, exist_ok=True)

            image_files = [f for f in os.listdir(original_folder) if f.lower().endswith(('png', 'jpg', 'jpeg'))]

            for img_file in image_files:
                img_path = os.path.join(original_folder, img_file)
                img = cv2.imread(img_path)
                if img is None:
                    print(f"❌ Erreur de lecture de l'image {img_file}")
                    continue

                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                for i in range(coeff):
                    augmented = augmentation(image=img)["image"]
                    new_img_path = os.path.join(augmented_folder, f"aug_{i}_{img_file}")
                    cv2.imwrite(new_img_path, cv2.cvtColor(augmented, cv2.COLOR_RGB2BGR))

    print("✅ Data Augmentation terminée avec succès !")

    image_data_new = []
    for folder in df_all_animals["Nom du dossier"]:
        folder_path_train = os.path.join(AUGMENTED_IMAGE_DIR, folder)
        num_images_train, avg_width_train, avg_height_train = get_image_info(folder_path_train)
        image_data_new.append([folder, num_images_train, avg_width_train, avg_height_train])

    image_data_new = pd.DataFrame(image_data_new,
                                  columns=["Nom du dossier", "Nombre d'images", "Largeur Moyenne", "Hauteur Moyenne"])

    df_metadata = pd.read_csv(METADATA_CSV_PATH)
    df_merged = pd.merge(image_data_new, df_metadata, left_on='Nom du dossier', right_on='Espèce anglais', how='left')

    df_merged.to_csv(MERGED_CSV_PATH, header=True)
    if print(df_merged['Espèce anglais'].isna().sum()):
        print("Toutes les lignes ont trouvé une correspondance")
    print("✅ Fusion des datasets terminée !")

    df_merged_spark = spark.createDataFrame(df_merged)

    df_dict = {}
    for dossier in df_merged_spark.select("Nom du dossier").distinct().rdd.flatMap(lambda x: x).collect():
        folder_path = os.path.join(AUGMENTED_IMAGE_DIR, dossier)
        if os.path.exists(folder_path):
            df_images = spark.createDataFrame(
                [(dossier, os.path.join(dossier, img)) for img in os.listdir(folder_path)],
                ["Nom du dossier", "Chemin Relatif"])
            df_dict[dossier] = df_images.join(df_merged_spark, on="Nom du dossier", how="left")

    for dossier, df in df_dict.items():
        df.write.mode("overwrite").parquet(os.path.join(PARQUET_OUTPUT_DIR, dossier))
        df.write.mode("overwrite").csv(os.path.join(CSV_OUTPUT_DIR, dossier))

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
        df.write.mode("overwrite").parquet(os.path.join(PARQUET_OUTPUT_DIR, dossier))
        df.write.mode("overwrite").csv(os.path.join(CSV_OUTPUT_DIR, dossier))

    if df_dict:
        df_final = reduce(DataFrame.unionAll, df_dict.values())
        df_final.write.mode("overwrite").parquet(os.path.join(PARQUET_OUTPUT_DIR, "all_images"))
        df_final.coalesce(1).write.mode("overwrite").csv(os.path.join(CSV_OUTPUT_DIR, "all_images"), header=True)
        print(f" Fusion complète ! Le DataFrame final contient {df_final.count()} images.")
    else:
        print("⚠️ Aucun DataFrame à fusionner !")

    print("✅ Partitionnement terminé.")

    df_existing = spark.read.jdbc(url=db_url, table="wildlens_etat", properties=db_properties)
    if df_existing.count() == 0:
        df_etat = spark.createDataFrame([
            Row(id_etat=1, type="train"),
            Row(id_etat=2, type="validation"),
            Row(id_etat=3, type="test")
        ])
        df_etat.write.mode("append").jdbc(url=db_url, table="wildlens_etat", properties=db_properties)

    df_existing = spark.read.jdbc(url=db_url, table="wildlens_facts", properties=db_properties)
    if df_existing.count() == 0:
        df_facts = df_final.select(
            "Espèce français", "Famille", "Nom latin", "Description", "Population estimée", "Localisation",
            "Espèce anglais", "Nombre d'images").dropDuplicates()

        df_facts = df_facts \
            .withColumnRenamed("Espèce anglais", "nom_en") \
            .withColumnRenamed("Population estimée", "population_estimee") \
            .withColumnRenamed("Nombre d'images", "nombre_image") \
            .withColumnRenamed("Espèce français", "nom_fr") \
            .withColumnRenamed("Nom latin", "nom_latin")

        df_facts = df_facts.withColumn("coeff_multiplication", lit(1))
        df_facts.write.jdbc(url=db_url, table="wildlens_facts", mode="append", properties=db_properties)

    # 🔄 Récupère la table facts pour obtenir les IDs d'espèce
    df_images = spark.read.jdbc(url=db_url, table="wildlens_facts", properties=db_properties)
    df_id_espece = df_images.select("id_espece", "nom_fr").distinct()

    # ✅ Garde uniquement les colonnes utiles pour wildlens_images
    df_final = df_final.select("Chemin Relatif", "Espèce français", "state")

    # 🔁 Jointure pour récupérer l'ID de l'espèce
    df_final = df_final.join(df_id_espece, df_final["Espèce français"] == df_id_espece["nom_fr"], "left")

    # 🧹 Nettoyage des colonnes inutiles
    df_final = df_final.drop("Espèce français").drop("nom_fr")

    # 🏷️ Renommage final des colonnes pour correspondre au schéma SQL
    df_final = df_final \
        .withColumnRenamed("Chemin Relatif", "image") \
        .withColumnRenamed("state", "id_etat")

    # ✅ Vérification du schéma juste avant insertion
    print("📋 Schéma final de df_final (wildlens_images) :")
    df_final.printSchema()
    df_final.show(5)

    # 📝 Écriture dans la table wildlens_images
    df_final.write.jdbc(url=db_url, table="wildlens_images", mode="append", properties=db_properties)
    print("✅ Table wildlens_images mise à jour avec succès !")

    spark.stop()
    print("🎉 Script terminé avec succès ! 🛑 SparkSession fermée.")
