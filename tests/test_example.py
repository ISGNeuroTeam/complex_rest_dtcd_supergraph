import json
from rest.test import TestCase, APIClient


class TestExample(TestCase):
    def setUp(self):
        """
        define instructions that will be executed before each test method
        """
        pass

    def test_hello(self):
        # How to make get requests
        client = APIClient()
        response = client.get('/complex_rest_dtcd_supergraph/v1/hello/'.lower())

        # checking status code
        self.assertEqual(response.status_code, 200)

        # checking body response
        message = response.data['message']
        self.assertEqual(message, 'Hello')

    def test_example(self):
        # How to make post requests
        client = APIClient()
        # post request with body: {'param1': 42, 'param2': 69}
        response = client.post(
            '/complex_rest_dtcd_supergraph/v1/example/'.lower(),
            json.dumps({'param1': 42, 'param2': 69}),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)
        message = response.data['message']
        self.assertIn('created successfully', message)
        body_params = response.data['body_params']
        self.assertEqual(body_params['param1'], 42)
        self.assertEqual(body_params['param2'], 69)

    def test_not_pass(self):
        self.assertEqual(1, 2, "Please, make some tests :)")

    def tearDown(self):
        """
        define instructions that will be executed after each test method
        """
        pass
