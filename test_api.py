import unittest
import random
import api

class TestAPI(unittest.TestCase):

    def setUp(self):
        api.app.testing = True
        self.app = api.app.test_client()

    def test_home(self):
        """
        Tests that the api is up and running
        """
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.decode(), "Hello, World!")

    def test_retrieve_client_info(self):
        """
        Tests that the api returns good value for checking if the client is part of the database or not
        """
        response_neg = self.app.get('/client_info?client_ID=100001') # non existing ID
        response_pos = self.app.get('/client_info?client_ID=100002') # existing ID
        self.assertEqual(response_neg.status_code, 200)
        self.assertEqual(response_pos.status_code, 200)
        self.assertFalse(response_neg.json)
        self.assertTrue(response_pos.json)

    def test_make_prediction_ID(self):
        """
        Tests that the api returns a float when asking for a score for an existing client
        """
        response = self.app.get('/predict/ID?client_ID=100002')
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json, float)

    def test_minimum_income(self):
        """
        Tests that the api is returning True if the client income is enough for a simulation
        Else returns False

        note : the parameters here are fixed and could raise some errors in the future
                since the minimum is set dynamically in the api
        """
        response_neg = self.app.get('/minimum_income?amt_income=10000')
        response_pos = self.app.get('/minimum_income?amt_income=100000')
        self.assertEqual(response_neg.status_code, 200)
        self.assertEqual(response_pos.status_code, 200)
        self.assertFalse(response_neg.json)
        self.assertTrue(response_pos.json)

    def test_maximum_income(self):
        """
        Tests that the api is returning True if the client income is not too much for a simulation
        Else returns False

        note : the parameters here are fixed and could raise some errors in the future
                since the maximum is set dynamically in the api
        """
        response_neg = self.app.get('/maximum_income?amt_income=20000000')
        response_pos = self.app.get('/maximum_income?amt_income=2000000')
        self.assertEqual(response_neg.status_code, 200)
        self.assertEqual(response_pos.status_code, 200)
        self.assertFalse(response_neg.json)
        self.assertTrue(response_pos.json)

    def test_make_prediction_noID(self):
        """
        Tests that api correctly receives informations for a non existing client
        And proceeds to make a prediction, then returning a float
        Tests both predicting routes
        """
        response_mandatory = self.app.get('/predict/mandatory?amt_income=50000&amt_goods_price=50000&amt_credit=50000&amt_annuity=50000')
        response_optional = self.app.get('/predict/optional?amt_income=50000&amt_goods_price=50000&amt_credit=50000&amt_annuity=50000&gender=Monsieur&age=26&cnt_children=2&time_employment=10&own_car=Oui&own_realty=Oui')
        self.assertEqual(response_mandatory.status_code, 200)
        self.assertEqual(response_optional.status_code, 200)
        self.assertIsInstance(response_mandatory.json, float)
        self.assertIsInstance(response_optional.json, float)
    
    def test_data_retrieval(self):
        """
        Tests the 3 routes allowing to retrieve informations for an existing client
        """
        response_income = self.app.get('/compare/ID/client_income?client_ID=100002')
        response_credit = self.app.get('/compare/ID/client_credit?client_ID=100002')
        response_annuity = self.app.get('/compare/ID/client_annuity?client_ID=100002')
        self.assertEqual(response_income.status_code, 200)
        self.assertEqual(response_credit.status_code, 200)
        self.assertEqual(response_annuity.status_code, 200)
        self.assertIsInstance(response_income.json, float)
        self.assertIsInstance(response_credit.json, float)
        self.assertIsInstance(response_annuity.json, float)
        
    def test_distribution_income(self):
        """
        Tests that the api is sending a list when asking for the income distribution
        Also tests that its elements are floats
        """
        response_distribution = self.app.get('/compare/distribution_income')
        self.assertEqual(response_distribution.status_code, 200)
        self.assertIsInstance(response_distribution.json, list)
        rand_elements = random.sample(response_distribution.json, 5)
        for i in rand_elements :
            self.assertIsInstance(i, float)

    def test_distribution_credit(self):
        """
        Tests that the api is sending a list when asking for the credit distribution
        Also tests that its elements are floats
        """
        response_distribution = self.app.get('/compare/distribution_credit')
        self.assertEqual(response_distribution.status_code, 200)
        self.assertIsInstance(response_distribution.json, list)
        rand_elements = random.sample(response_distribution.json, 5)
        for i in rand_elements :
            self.assertIsInstance(i, float)

    def test_distribution_annuity(self):
        """
        Tests that the api is sending a list when asking for the annuity distribution
        Also tests that its elements are floats
        """
        response_distribution = self.app.get('/compare/distribution_annuity')
        self.assertEqual(response_distribution.status_code, 200)
        self.assertIsInstance(response_distribution.json, list)
        rand_elements = random.sample(response_distribution.json, 5)
        for i in rand_elements :
            self.assertIsInstance(i, float)

    def test_metric_1_retrieval(self):
        """
        Tests that the api is sending a float when asking for metric m1
        """
        response = self.app.get('/compare/metric_1?amt_income=50000')
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json, float)

    def test_metric_2_retrieval(self):
        """
        Tests that the api is sending a float when asking for metric m2
        """
        response = self.app.get('/compare/metric_2?amt_income=50000')
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json, float)

    def test_metric_3_retrieval(self):
        """
        Tests that the api is sending a float when asking for metric m3
        """
        response = self.app.get('/compare/metric_3?amt_income=50000')
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json, float)

if __name__ == '__main__':
    unittest.main()