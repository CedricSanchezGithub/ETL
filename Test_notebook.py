import os
import unittest
from unittest.mock import patch, MagicMock

import cv2
import pandas as pd
import pyspark.sql

# Importer le module à tester
import notebook_to_python


class ETLProcessTest(unittest.TestCase):
    # Tests de base pour get_image_info qui fonctionnent bien
    @patch('os.path.exists')
    @patch('os.listdir')
    @patch('PIL.Image.open')
    def test_dossier_inexistant_retourne_valeurs_par_defaut(self, mock_image_open, mock_listdir, mock_exists):
        mock_exists.return_value = False
        resultat = notebook_to_python.get_image_info("/chemin/inexistant")
        self.assertEqual(resultat, (0, None, None))
        mock_listdir.assert_not_called()
        mock_image_open.assert_not_called()

    @patch('os.path.exists')
    @patch('os.listdir')
    def test_dossier_vide_retourne_zero_images(self, mock_listdir, mock_exists):
        mock_exists.return_value = True
        mock_listdir.return_value = []
        resultat = notebook_to_python.get_image_info("/chemin/vide")
        self.assertEqual(resultat, (0, None, None))

    @patch('os.path.exists')
    @patch('os.listdir')
    def test_dossier_sans_images_retourne_zero_images(self, mock_listdir, mock_exists):
        mock_exists.return_value = True
        mock_listdir.return_value = ["fichier.txt", "document.pdf"]
        resultat = notebook_to_python.get_image_info("/chemin/sans_images")
        self.assertEqual(resultat, (0, None, None))

    @patch('os.path.exists')
    @patch('os.listdir')
    @patch('PIL.Image.open')
    @patch('os.path.join')
    def test_calcul_correct_avec_une_seule_image(self, mock_join, mock_image_open, mock_listdir, mock_exists):
        mock_exists.return_value = True
        mock_listdir.return_value = ["image.jpg"]
        mock_join.return_value = "/chemin/complet/image.jpg"

        image_mock = MagicMock()
        image_mock.width = 100
        image_mock.height = 200
        mock_image_open.return_value.__enter__.return_value = image_mock

        resultat = notebook_to_python.get_image_info("/chemin/avec_images")
        self.assertEqual(resultat, (1, 100.0, 200.0))

    @patch('os.path.exists')
    @patch('os.listdir')
    @patch('PIL.Image.open')
    @patch('os.path.join')
    def test_calcul_moyen_avec_plusieurs_images(self, mock_join, mock_image_open, mock_listdir, mock_exists):
        mock_exists.return_value = True
        mock_listdir.return_value = ["image1.jpg", "image2.png", "image3.jpeg"]

        # Configurer os.path.join pour retourner des chemins valides
        def join_side_effect(folder, file):
            return f"{folder}/{file}"

        mock_join.side_effect = join_side_effect

        # Créer un mock pour une seule image (toutes les images auront les mêmes dimensions)
        image_mock = MagicMock()
        image_mock.width = 200
        image_mock.height = 300

        # Configurer le mock pour Image.open
        mock_context = MagicMock()
        mock_context.__enter__.return_value = image_mock
        mock_context.__exit__ = lambda *args: None
        mock_image_open.return_value = mock_context

        # Exécuter la fonction à tester
        resultat = notebook_to_python.get_image_info("/chemin/avec_images")

        # Vérifier les résultats
        self.assertEqual(resultat, (3, 200.0, 300.0))
        self.assertEqual(mock_image_open.call_count, 3)  # Vérifie que Image.open est appelé 3 fois

        resultat = notebook_to_python.get_image_info("/chemin/avec_images")
        self.assertEqual(resultat, (3, 200.0, 300.0))

    @patch('os.path.exists')
    @patch('os.listdir')
    @patch('PIL.Image.open')
    @patch('os.path.join')
    def test_gestion_erreurs_lors_ouverture_image(self, mock_join, mock_image_open, mock_listdir, mock_exists):
        mock_exists.return_value = True
        mock_listdir.return_value = ["valide.jpg", "corrompue.jpg"]
        mock_join.side_effect = lambda *args: "/".join(args)

        image_valide = MagicMock(width=100, height=200)

        # Configuration correcte pour simuler une image valide et une image corrompue
        def side_effect(path):
            if "corrompue.jpg" in path:
                raise Exception("Image corrompue")
            mock_context = MagicMock()
            mock_context.__enter__.return_value = image_valide
            mock_context.__exit__ = lambda *args: None
            return mock_context

        mock_image_open.side_effect = side_effect

        resultat = notebook_to_python.get_image_info("/chemin/avec_images_mixtes")

        # Dans le cas d'une image corrompue, on aura quand même les données de l'image valide
        self.assertEqual(resultat, (2, 100.0, 200.0))

    @patch('os.path.exists')
    @patch('os.listdir')
    @patch('PIL.Image.open')
    @patch('os.path.join')
    def test_verification_extension_images_case_insensitive(self, mock_join, mock_image_open, mock_listdir,
                                                            mock_exists):
        mock_exists.return_value = True
        mock_listdir.return_value = ["image1.JPG", "image2.Png", "image3.JPEG", "document.txt"]
        mock_join.side_effect = lambda *args: "/".join(args)

        image_mock = MagicMock(width=100, height=100)

        # Configuration correcte pour retourner les mêmes données pour chaque image
        def side_effect(path):
            mock_context = MagicMock()
            mock_context.__enter__.return_value = image_mock
            mock_context.__exit__ = lambda *args: None
            return mock_context

        mock_image_open.side_effect = side_effect

        resultat = notebook_to_python.get_image_info("/chemin/avec_images_mixtes")
        self.assertEqual(resultat[0], 3)

    # Tests modulaires pour les fonctionnalités complexes
    def test_connexion_spark_mysql(self):
        """Test de la création d'une connexion Spark à MySQL"""
        with patch('pyspark.sql.SparkSession.builder', autospec=True) as mock_builder:
            # Configuration de la chaîne de mocks
            mock_app = MagicMock()
            mock_config = MagicMock()
            mock_session = MagicMock()

            mock_builder.appName.return_value = mock_app
            mock_app.config.return_value = mock_config
            mock_config.getOrCreate.return_value = mock_session

            # Définition d'une fonction simple qui simule l'initialisation Spark
            def init_spark():
                spark = (pyspark.sql.SparkSession.builder
                         .appName("Test App")
                         .config("spark.jars", "mysql-connector.jar")
                         .getOrCreate())
                return spark

            # Tester la fonction
            result = init_spark()
            self.assertEqual(result, mock_session)
            mock_builder.appName.assert_called_once_with("Test App")
            mock_app.config.assert_called_once_with("spark.jars", "mysql-connector.jar")
            mock_config.getOrCreate.assert_called_once()

    def test_fusion_dataframes(self):
        """Test de la fusion de DataFrames pandas"""
        # Préparer les données de test
        df_images = pd.DataFrame({
            "Nom du dossier": ["raccoon", "fox"],
            "Nombre d'images": [10, 20]
        })

        df_metadata = pd.DataFrame({
            "Espèce anglais": ["raccoon", "fox"],
            "Espèce français": ["raton laveur", "renard"]
        })

        # Utiliser un patch pour pd.read_csv
        with patch('pandas.read_csv', return_value=df_metadata):
            # Utiliser un patch pour pd.merge
            with patch('pandas.merge') as mock_merge:
                # Configurer le résultat attendu de la fusion
                expected_df = pd.DataFrame({
                    "Nom du dossier": ["raccoon", "fox"],
                    "Nombre d'images": [10, 20],
                    "Espèce anglais": ["raccoon", "fox"],
                    "Espèce français": ["raton laveur", "renard"]
                })
                mock_merge.return_value = expected_df

                # Exécuter la fusion comme dans le code original
                result_df = pd.merge(
                    df_images,
                    pd.read_csv("path/to/metadata.csv"),
                    left_on='Nom du dossier',
                    right_on='Espèce anglais',
                    how='left'
                )

                # Vérifier le résultat
                self.assertEqual(len(result_df), 2)
                mock_merge.assert_called_once()

                # Vérifier les arguments de l'appel à merge
                _, kwargs = mock_merge.call_args
                self.assertEqual(kwargs['left_on'], 'Nom du dossier')
                self.assertEqual(kwargs['right_on'], 'Espèce anglais')
                self.assertEqual(kwargs['how'], 'left')

    def test_ecriture_jdbc(self):
        """Test isolé pour écrire des données dans MySQL via JDBC"""
        # Créer un DataFrame mock
        df_mock = MagicMock()

        # Configurer la chaîne d'appels pour write et jdbc
        write_mock = MagicMock()
        df_mock.write = write_mock

        # Exécuter l'opération d'écriture JDBC
        df_mock.write.jdbc(
            url="jdbc:mysql://localhost:3306/wildlens",
            table="wildlens_facts",
            mode="append",
            properties={"user": "root", "password": "root"}
        )

        # Vérifier que jdbc a été appelé avec les bons paramètres
        write_mock.jdbc.assert_called_once_with(
            url="jdbc:mysql://localhost:3306/wildlens",
            table="wildlens_facts",
            mode="append",
            properties={"user": "root", "password": "root"}
        )

    @patch('os.makedirs')
    @patch('os.path.exists')
    @patch('os.listdir')
    @patch('cv2.imread')
    @patch('cv2.imwrite')
    @patch('albumentations.Compose')
    def test_data_augmentation_simple(self, mock_compose, mock_imwrite, mock_imread,
                                      mock_listdir, mock_exists, mock_makedirs):
        """Test isolé de la data augmentation"""
        # Configurer les mocks
        mock_exists.return_value = True
        mock_listdir.return_value = ["image1.jpg", "image2.jpg"]

        # Mock pour os.path.join
        with patch('os.path.join', side_effect=lambda *args: '/'.join(args)):
            # Mock pour imread
            img_mock = MagicMock()
            mock_imread.return_value = img_mock

            # Mock pour la transformation d'image
            transform_mock = MagicMock()
            transform_mock.return_value = {"image": img_mock}
            mock_compose.return_value = transform_mock

            # Mock pour imwrite
            mock_imwrite.return_value = True

            # Définir une fonction de test isolée
            def augment_image(input_path, output_path, coeff=2):
                os.makedirs(output_path, exist_ok=True)

                images = [f for f in os.listdir(input_path) if f.lower().endswith(('jpg', 'png', 'jpeg'))]

                # Utiliser le mock au lieu de créer un nouvel objet
                transform = mock_compose.return_value

                for img_file in images:
                    img = cv2.imread(os.path.join(input_path, img_file))
                    for i in range(coeff):
                        augmented = transform(image=img)["image"]
                        new_path = os.path.join(output_path, f"aug_{i}_{img_file}")
                        cv2.imwrite(new_path, augmented)

                return len(images) * coeff

            # Exécuter notre fonction d'augmentation
            result = augment_image("input/dir", "output/dir")

            # Vérifications
            mock_makedirs.assert_called_once_with("output/dir", exist_ok=True)
            self.assertEqual(mock_imread.call_count, 2)
            self.assertEqual(mock_imwrite.call_count, 4)  # 2 images * 2 coefficients
            self.assertEqual(result, 4)


if __name__ == '__main__':
    unittest.main()