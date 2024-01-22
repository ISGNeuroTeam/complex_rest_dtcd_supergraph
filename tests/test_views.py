from random import randint

from django.test import TestCase
from rest_framework.test import APIClient


# current tests do run with running complex rest with attached supergraph plugin
# so in order to run these tests user needs to run complex rest Django test suite
# with current tests folder mentioned as a parameter
class GraphViewTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_get(self):
        response = self.client.get('/complex_rest_dtcd_supergraph/v1/graphs/')
        self.assertEqual(response.status_code, 200)

    def test_post(self):
        data = {'graph': 'some graph data'}
        response = self.client.post('/complex_rest_dtcd_supergraph/v1/graphs/', data)
        self.assertEqual(response.status_code, 400)
        random: int = randint(0, 1000)
        data = {'graph': 'some graph data', 'title': f'some-new-graph-{random}'}
        response = self.client.post('/complex_rest_dtcd_supergraph/v1/graphs/', data)
        self.assertEqual(response.status_code, 200)
        self.graph_id = response.data['result']['graph_id']
        # clean up
        self.client.delete(f'/complex_rest_dtcd_supergraph/v1/graphs/{self.graph_id}/')


class GraphDetailViewTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_all(self) -> None:
        #     create test graph
        random: int = randint(0, 1000)
        data = {'graph': 'some graph data', 'title': f'some-new-graph-{random}'}
        response = self.client.post('/complex_rest_dtcd_supergraph/v1/graphs/', data)
        self.graph_id = response.data['result']['graph_id']
        # test get
        response = self.client.get(f'/complex_rest_dtcd_supergraph/v1/graphs/{self.graph_id}/')
        self.assertEqual(response.status_code, 200)
        # test put
        data = {'graph': 'updated graph data'}
        response = self.client.put(f'/complex_rest_dtcd_supergraph/v1/graphs/{self.graph_id}/', data)
        self.assertEqual(response.status_code, 200)
         # test delete
        response = self.client.delete(f'/complex_rest_dtcd_supergraph/v1/graphs/{self.graph_id}/')
        self.assertEqual(response.status_code, 200)
