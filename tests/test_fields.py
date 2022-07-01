import unittest

from django.test import SimpleTestCase, tag
from rest_framework.validators import ValidationError

from complex_rest_dtcd_supergraph.fields import EdgeField, VertexField

from .misc import KEYS


class TestVertexField(SimpleTestCase):
    def test_invalid(self):
        # missing ID key
        data = {"spam": 42}
        field = VertexField()

        with self.assertRaises(ValidationError):
            field.to_internal_value(data)


class TestEdgeField(SimpleTestCase):
    def test_invalid(self):
        data = {"spam": 42}
        field = EdgeField()

        with self.assertRaises(ValidationError):
            field.to_internal_value(data)

        # missing: end vertex, start/end ports
        data[KEYS["source_node"]] = "n1"
        with self.assertRaises(ValidationError):
            field.to_internal_value(data)

        # missing: start/end ports
        data[KEYS["target_node"]] = "n2"
        with self.assertRaises(ValidationError):
            field.to_internal_value(data)

        # missing: end port
        data[KEYS["source_port"]] = "p1"
        with self.assertRaises(ValidationError):
            field.to_internal_value(data)


if __name__ == "__main__":
    unittest.main()
