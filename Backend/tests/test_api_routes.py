import os
import unittest
from flask import Flask
from Backend.routes.api_routes import api


class ApiRoutesTestCase(unittest.TestCase):
    def setUp(self):
        # Configuration de l'application Flask pour les tests
        self.app = Flask(__name__)
        self.app.register_blueprint(api)
        self.client = self.app.test_client()

        # Configuration de la clé API pour les tests
        os.environ["API_KEY"] = "testkey"
        self.auth_headers = {"Authorization": "Bearer testkey"}

    def test_index(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"APScheduler", response.data)

    def test_trigger_pipeline_etl(self):
        response = self.client.get("/triggermspr", headers=self.auth_headers)
        self.assertIn(response.status_code, [200, 500])

    def test_trigger_pipeline_metadata(self):
        response = self.client.get("/triggermetadata", headers=self.auth_headers)
        self.assertIn(response.status_code, [200, 500])

    def test_get_especes(self):
        response = self.client.get("/api/especes", headers=self.auth_headers)
        self.assertIn(response.status_code, [200, 500])

    def test_get_all_metadata(self):
        response = self.client.get("/api/metadata", headers=self.auth_headers)
        self.assertIn(response.status_code, [200, 500])

    def test_get_images_by_species_no_param(self):
        response = self.client.get("/api/images", headers=self.auth_headers)
        self.assertEqual(response.status_code, 400)
        self.assertIn(b"espece", response.data)

    def test_trigger_pipeline_etl_auth(self):
        # Sans header
        response = self.client.get("/triggermspr")
        self.assertEqual(response.status_code, 401)
        # Mauvaise clé
        response = self.client.get("/triggermspr", headers={"Authorization": "Bearer wrong"})
        self.assertEqual(response.status_code, 403)
        # Bonne clé
        response = self.client.get("/triggermspr", headers=self.auth_headers)
        self.assertIn(response.status_code, [200, 500])

    def test_trigger_pipeline_metadata_auth(self):
        response = self.client.get("/triggermetadata")
        self.assertEqual(response.status_code, 401)
        response = self.client.get("/triggermetadata", headers={"Authorization": "Bearer wrong"})
        self.assertEqual(response.status_code, 403)
        response = self.client.get("/triggermetadata", headers=self.auth_headers)
        self.assertIn(response.status_code, [200, 500])

    def test_photo_download_auth(self):
        # Pas de header
        response = self.client.post("/photo_download")
        self.assertEqual(response.status_code, 401)
        # Mauvaise clé
        response = self.client.post("/photo_download", headers={"Authorization": "Bearer wrong"})
        self.assertEqual(response.status_code, 403)
        # Bonne clé avec fichier factice
        data = {"file": (b"fake", "test.jpg")}
        response = self.client.post("/photo_download", headers=self.auth_headers, data=data)
        self.assertIn(response.status_code, [200, 400])


if __name__ == "__main__":
    unittest.main()
