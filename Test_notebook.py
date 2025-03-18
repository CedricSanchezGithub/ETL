import unittest
from unittest.mock import patch

import notebook_to_python


class GetImageInfoTest(unittest.TestCase):

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

        image_mock = unittest.mock.MagicMock()
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
        mock_join.side_effect = lambda *args: "/".join(args)

        images = [
            unittest.mock.MagicMock(width=100, height=200),
            unittest.mock.MagicMock(width=200, height=300),
            unittest.mock.MagicMock(width=300, height=400)
        ]

        mock_image_open.return_value.__enter__.side_effect = images

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

        image_valide = unittest.mock.MagicMock()
        image_valide.width = 100
        image_valide.height = 200

        # Configurer le mock pour lever une exception sur la deuxième image
        def mock_side_effect(path):
            if "corrompue.jpg" in path:
                raise Exception("Image corrompue")
            mock_context = unittest.mock.MagicMock()
            mock_context.__enter__.return_value = image_valide
            return mock_context

        mock_image_open.side_effect = mock_side_effect

        resultat = notebook_to_python.get_image_info("/chemin/avec_images_mixtes")

        # Il y a deux images, mais une seule est valide
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

        image_mock = unittest.mock.MagicMock(width=100, height=100)
        mock_image_open.return_value.__enter__.return_value = image_mock

        resultat = notebook_to_python.get_image_info("/chemin/avec_images_mixtes")

        self.assertEqual(resultat[0], 3)  # 3 images reconnues malgré la casse