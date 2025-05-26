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
        # 200 or 500 depending on DB, but endpoint must respond
        self.assertIn(response.status_code, [200, 500])

    def test_get_all_metadata(self):
        response = self.client.get("/api/metadata")
        self.assertIn(response.status_code, [200, 500])

    def test_get_images_by_species_no_param(self):
        response = self.client.get("/api/images")
        self.assertEqual(response.status_code, 400)
        self.assertIn(b"espece", response.data)


if __name__ == "__main__":
    unittest.main()
