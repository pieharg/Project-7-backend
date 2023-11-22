import unittest
import api

class TestAPI(unittest.TestCase):

    def setUp(self):
        api.app.testing = True
        self.app = api.app.test_client()

    def test_home(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.decode(), "Hello, World!")

    def test_retrieve_client_info(self):
        response_neg = self.app.get('/client_info?client_ID=100001') # random non existing ID
        response_pos = self.app.get('/client_info?client_ID=100002') # random existing ID
        self.assertEqual(response_neg.status_code, 200)
        self.assertEqual(response_pos.status_code, 200)
        self.assertFalse(response_neg.json)
        self.assertTrue(response_pos.json)

    def test_make_prediction_ID(self):
        response = self.app.get('/predict/ID?client_ID=100002')
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json, float)

    def test_make_prediction_noID(self):
        #random request
        response = self.app.get('/predict/noID?gender=Monsieur&age=26&cnt_children=2&time_employment=10&income=41050&own_car=Oui&own_realty=Oui&amt_goods_price=5156&amt_credit=26515&amt_annuity=1650')
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json, float)
    
    # je ne teste pas toutes les routes car elles sont intrinsèquement construites de la même manière
    def test_data_income(self):
        response = self.app.get('/comparison/ID/graph_income?client_ID=100002')
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json["income"], float)
        self.assertIsInstance(response.json["data"], list)
        for single in response.json["data"]:
            self.assertIsInstance(single, float)

    def test_metrics(self):
        response = self.app.get('/comparison/ID/metrics?client_ID=100002')
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json["metrics"], list)
        for single in response.json["metrics"]:
            self.assertIsInstance(single, float)

    def test_data_income_noID(self):
        response = self.app.get('/comparison/noID/graph_income')
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json["data"], list)
        for single in response.json["data"]:
            self.assertIsInstance(single, float)

    def test_metrics_noID(self):
        response = self.app.get('/comparison/noID/metrics?income=50000') # random income
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json["metrics"], list)
        for single in response.json["metrics"]:
            self.assertIsInstance(single, float)

if __name__ == '__main__':
    unittest.main()