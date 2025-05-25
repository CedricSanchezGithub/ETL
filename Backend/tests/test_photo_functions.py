import os
import shutil
import tempfile
import unittest
from unittest.mock import MagicMock, patch

from flask import request

from Backend.routes.api_routes import photo_save
from Backend.tests.fixtures.flask_test_app import mock_app


class TestPhotoUploadFunctions(unittest.TestCase):
    """Tests unitaires pour les fonctions liées au téléchargement de photos."""

    def setUp(self):
        """Configuration avant chaque test."""
        # Créer un dossier temporaire pour les tests
        self.test_dir = tempfile.mkdtemp()
        # Remplacer le chemin photo_save par notre dossier temporaire
        self.original_photo_save = photo_save
        # Ne pas modifier la valeur réelle, on va utiliser un patch

    def tearDown(self):
        """Nettoyage après chaque test."""
        # Supprimer le dossier temporaire
        shutil.rmtree(self.test_dir)

    @patch("Backend.routes.api_routes.photo_save")
    @patch("Backend.routes.api_routes.os.path.join")
    @patch("Backend.routes.api_routes.os")
    def test_file_saving(self, mock_os, mock_join, mock_photo_save):
        """Teste que les fichiers sont correctement enregistrés."""
        from Backend.routes.api_routes import photo_download

        # Configurer les mocks
        mock_photo_save.__str__.return_value = self.test_dir
        mock_join.return_value = os.path.join(self.test_dir, "test_image.jpg")
        mock_os.path.exists.return_value = True

        # Créer un fichier temporaire pour simuler l'upload
        with tempfile.NamedTemporaryFile(suffix=".jpg") as temp_file:
            temp_file.write(b"test content")
            temp_file.flush()

            # Créer un mock pour request.files
            mock_files = {
                "file": MagicMock(filename="test_image.jpg", save=MagicMock())
            }

            # Utiliser un contexte de requête Flask pour le test
            app = mock_app.get_app()
            with app.test_request_context(method='POST'):
                # Utiliser un patch object directement sur request.files
                with patch.object(request, 'files', mock_files):
                    photo_download()

            # Vérifier que la fonction save a été appelée
            mock_files["file"].save.assert_called_once()

    def test_valid_file_extensions(self):
        """Teste la validation des extensions de fichiers."""
        from Backend.routes.api_routes import photo_download

        # Utiliser un contexte de requête Flask pour le test
        app = mock_app.get_app()
        
        # Tester une extension valide
        with app.test_request_context(method='POST'):
            mock_files = {"file": MagicMock(filename="valid_image.jpg")}
            with patch.object(request, 'files', mock_files):
                with patch.object(mock_files["file"], "save"):
                    result = photo_download()
                    self.assertNotIn("error", result[0].json)

        # Tester une extension valide (png)
        with app.test_request_context(method='POST'):
            mock_files = {"file": MagicMock(filename="valid_image.png")}
            with patch.object(request, 'files', mock_files):
                with patch.object(mock_files["file"], "save"):
                    result = photo_download()
                    self.assertNotIn("error", result[0].json)

        # Tester une extension invalide
        with app.test_request_context(method='POST'):
            mock_files = {"file": MagicMock(filename="invalid_file.txt")}
            with patch.object(request, 'files', mock_files):
                result = photo_download()
                self.assertIn("error", result[0].json)
                self.assertEqual(result[1], 400)  # Vérifier le code de statut

        # Tester un nom de fichier sans extension
        with app.test_request_context(method='POST'):
            mock_files = {"file": MagicMock(filename="no_extension")}
            with patch.object(request, 'files', mock_files):
                result = photo_download()
                self.assertIn("error", result[0].json)
                self.assertEqual(result[1], 400)
            result = photo_download()
            self.assertIn("error", result[0].json)
            self.assertEqual(result[1], 400)


if __name__ == "__main__":
    unittest.main()
