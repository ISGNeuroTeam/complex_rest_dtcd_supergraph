"""
Custom fields.
"""

from django.utils.translation import gettext_lazy as _
from rest_framework.serializers import DictField

from .settings import SCHEMA


class GraphField(DictField):
    """Graph representation."""

    KEYS = ("nodes", "edges")  # TODO get these from config
    default_error_messages = {
        "key_error": _("Key '{value}' is missing."),
    }

    def to_representation(self, value):
        """Convert to primitive, serializable data types."""
        # TODO add Converter inside .to_representation()
        return super().to_representation(value)

    def to_internal_value(self, data: dict):
        """Dict with graph in exchange format <- dict of primitive datatypes."""

        data = super().to_internal_value(data)

        # make sure keys are present
        for key in self.KEYS:
            if key not in data:
                self.fail("key_error", value=key)

        # TODO construct graphs from data
        # TODO use with Converter?

        return data


class VertexField(DictField):
    """A vertex dictionary representation.

    Validates the vertex to have an ID field.
    """

    default_error_messages = {
        "key_error": _("Key '{value}' is missing."),
    }

    id_key = SCHEMA["keys"]["yfiles_id"]

    def to_internal_value(self, data: dict):
        data = super().to_internal_value(data)

        if self.id_key not in data:
            self.fail("key_error", value=self.id_key)

        return data


class EdgeField(DictField):
    """An edge dictionary representation.

    Validates the edge to have start and end vertices and ports.
    """

    default_error_messages = {
        "key_error": _("Key '{value}' is missing."),
    }

    src_node_key = SCHEMA["keys"]["source_node"]
    tgt_node_key = SCHEMA["keys"]["target_node"]
    src_port_key = SCHEMA["keys"]["source_port"]
    tgt_port_key = SCHEMA["keys"]["target_port"]
    keys = (
        src_node_key,
        tgt_node_key,
        src_port_key,
        tgt_port_key,
    )

    def to_internal_value(self, data: dict):
        data = super().to_internal_value(data)

        for key in self.keys:
            if key not in data:
                self.fail("key_error", value=key)

        return data
