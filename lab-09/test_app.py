import unittest

from app import app


class TestApp(unittest.TestCase):
    def test_home(self):
        with app.test_client() as client:
            response = client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.get_data(as_text=True), "Hello, Jenkins Multi-Stage Pipeline!"
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
