"""
Custom fields.
"""

import uuid

from django.utils.translation import gettext_lazy as _
from rest_framework.serializers import DictField, UUIDField

from .settings import KEYS


class ContainsOrFailMixin:
    default_error_messages = {
        "key_error": _("Key '{value}' is missing."),
    }

    def _contains_or_fail(self, data: dict, key):
        if key not in data:
            self.fail("key_error", value=key)


class CustomUUIDFIeld(UUIDField):
    """A field that ensures the input is a valid UUID string.

    Overloads `to_representation` to work with UUIDs in hex string format.
    """

    def to_representation(self, value):
        # if string, try to convert to UUID first
        if isinstance(value, str):
            try:
                value = uuid.UUID(hex=value)
            except:
                self.fail("invalid", value=value)

        return super().to_representation(value)


class VertexField(ContainsOrFailMixin, DictField):
    """A vertex dictionary representation.

    Validates the vertex to have an ID field.
    """

    id_key = KEYS.yfiles_id

    def to_internal_value(self, data: dict):
        data = super().to_internal_value(data)
        self._contains_or_fail(data, self.id_key)

        return data


class GroupField(VertexField):
    """A group representation."""


class EdgeField(ContainsOrFailMixin, DictField):
    """An edge dictionary representation.

    Validates the edge to have start and end vertices and ports.
    """

    keys = (
        KEYS.source_node,
        KEYS.target_node,
        KEYS.source_port,
        KEYS.target_port,
    )

    def to_internal_value(self, data):
        data = super().to_internal_value(data)

        for key in self.keys:
            self._contains_or_fail(data, key)

        return data
