import unittest

from flask import Flask

from Backend.routes.api_routes import api


class ApiRoutesTestCase(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.register_blueprint(api)
        self.client = self.app.test_client()

    def test_index(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"APScheduler", response.data)

    def test_trigger_pipeline_etl(self):
        response = self.client.get("/triggermspr")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Pipeline ETL", response.data)

    def test_trigger_pipeline_metadata(self):
        response = self.client.get("/triggermetadata")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Pipeline Metadata", response.data)

    def test_get_especes(self):
        response = self.client.get("/api/especes")
        self.assertIn(response.status_code, [200, 500])

    def test_get_all_metadata(self):
        response = self.client.get("/api/metadata")
        self.assertIn(response.status_code, [200, 500])

    def test_get_images_by_species_no_param(self):
        response = self.client.get("/api/images")
        self.assertEqual(response.status_code, 400)
        self.assertIn(b"espece", response.data)

    def test_trigger_pipeline_etl_auth(self):
        # Test sans header
        response = self.client.get("/triggermspr")
        self.assertEqual(response.status_code, 401)
        # Test avec mauvaise clé
        response = self.client.get(
            "/triggermspr", headers={"Authorization": "Bearer wrong"}
        )
        self.assertEqual(response.status_code, 403)
        # Test avec bonne clé
        import os

        os.environ["API_KEY"] = "testkey"
        response = self.client.get(
            "/triggermspr", headers={"Authorization": "Bearer testkey"}
        )
        self.assertIn(response.status_code, [200, 500])

    def test_trigger_pipeline_metadata_auth(self):
        response = self.client.get("/triggermetadata")
        self.assertEqual(response.status_code, 401)
        response = self.client.get(
            "/triggermetadata", headers={"Authorization": "Bearer wrong"}
        )
        self.assertEqual(response.status_code, 403)
        import os

        os.environ["API_KEY"] = "testkey"
        response = self.client.get(
            "/triggermetadata", headers={"Authorization": "Bearer testkey"}
        )
        self.assertIn(response.status_code, [200, 500])

    def test_photo_download_auth(self):
        response = self.client.post("/photo_download")
        self.assertEqual(response.status_code, 401)
        response = self.client.post(
            "/photo_download", headers={"Authorization": "Bearer wrong"}
        )
        self.assertEqual(response.status_code, 403)
        import os

        os.environ["API_KEY"] = "testkey"
        # Envoi d'un fichier factice pour le test
        data = {"file": (b"fake", "test.jpg")}
        response = self.client.post(
            "/photo_download", headers={"Authorization": "Bearer testkey"}, data=data
        )
        self.assertIn(response.status_code, [200, 400])


if __name__ == "__main__":
    unittest.main()
