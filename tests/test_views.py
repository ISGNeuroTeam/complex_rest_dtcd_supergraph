import unittest
from pathlib import Path
from pprint import pformat
from types import SimpleNamespace

import dictdiffer
from django.urls import reverse
from django.test import Client, tag
from rest_framework import status
from rest_framework.test import APISimpleTestCase

from .misc import load_data, sort_payload

TEST_DIR = Path(__file__).resolve().parent
CLIENT = Client()

# DEBUG
DEBUG_FILEPATH = "debug.txt"


class APITestCaseMixin:
    """Some common attributes and methods for API tests.

    The idea: send an HTTP requests to a URL endpoint, get the response
    and check the status.
    """

    expected_status = SimpleNamespace(
        get=status.HTTP_200_OK,
        post=status.HTTP_201_CREATED,
        put=status.HTTP_200_OK,  # or 204; 201 if created
        delete=status.HTTP_200_OK,  # 202 on queue, 204 on noDATA_DIR = TEST_DIR / "data"
        URL_RESET=reverse("supergraph:reset")  # post here resets the db content
    )
    url = None  # the URL endpoint to check

    def get(self):
        """Send `GET` request to `self.url`, validate status and return
        the response.
        """

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, self.expected_status.get)
        return response

    def post(self, data: dict):
        """Send `POST` request with given data in JSON format to
        `self.url`, validate status and return the response.
        """

        response = self.client.post(self.url, data=data, format="json")
        self.assertEqual(response.status_code, self.expected_status.post)
        return response

    def put(self, data: dict):
        """Send `PUT` request with given data in JSON format to
        `self.url`, validate status and return the response.
        """

        response = self.client.put(self.url, data=data, format="json")
        self.assertEqual(response.status_code, self.expected_status.put)
        return response

    def delete(self):
        """Send `DELETE` request to `self.url`, validate status and return
        the response.
        """

        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, self.expected_status.delete)
        return response

    def _test_delete(self):
        """Simple implementation for delete endpoint.

        Calls `.delete()`, then gets the resource on the same URL and
        checks the status to be 404.
        """

        r1 = self.delete()
        r2 = self.client.get(self.url)  # note explicit request
        self.assertEqual(r2.status_code, status.HTTP_404_NOT_FOUND)

        return r1, r2


if __name__ == "__main__":
    unittest.main()
