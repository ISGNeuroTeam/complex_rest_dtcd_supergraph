"""
Custom fields.
"""

from copy import deepcopy
from types import SimpleNamespace

from django.utils.translation import gettext_lazy as _
from rest_framework.serializers import DictField

from .settings import SCHEMA
from .structures import Edge, Group, Port, Primitive, Vertex


class PopOrFailMixin:
    default_error_messages = {
        "key_error": _("Key '{value}' is missing."),
    }

    def _pop_or_fail(self, key, data: dict):
        try:
            return data.pop(key)
        except KeyError:
            self.fail("key_error", value=key)


class PrimitiveField(PopOrFailMixin, DictField):

    id_key = SCHEMA["keys"]["yfiles_id"]
    internal_value_class = Primitive

    def to_representation(self, value: Primitive):
        """Convert to primitive, serializable data types."""

        result = deepcopy(value.data)
        result[self.id_key] = value.uid

        return result

    def to_internal_value(self, data: dict):
        """Primitive <- dict of native values."""

        data = super().to_internal_value(data)
        data = deepcopy(data)
        uid = self._pop_or_fail(self.id_key, data)

        return self.internal_value_class(uid=uid, data=data)


class PortField(PrimitiveField):
    """A port representation."""

    internal_value_class = Port


class VertexField(PrimitiveField):
    """A vertex representation."""

    internal_value_class = Vertex


class GroupField(PrimitiveField):
    """A group representation."""

    internal_value_class = Group


class EdgeField(PopOrFailMixin, DictField):
    """An edge representation."""

    keys = SimpleNamespace(
        source=SCHEMA["keys"]["source_port"],
        target=SCHEMA["keys"]["target_port"],
    )

    def to_representation(self, value: Edge):
        """Convert to primitive, serializable data types."""

        result = deepcopy(value.data)
        result[self.keys.source] = value.start
        result[self.keys.target] = value.end

        return result

    def to_internal_value(self, data):
        """Edge <- dict of native values."""

        data = super().to_internal_value(data)
        data = deepcopy(data)
        start_port = self._pop_or_fail(self.keys.source, data)
        end_port = self._pop_or_fail(self.keys.target, data)

        return Edge(
            start=start_port,
            end=end_port,
            data=data,
        )
