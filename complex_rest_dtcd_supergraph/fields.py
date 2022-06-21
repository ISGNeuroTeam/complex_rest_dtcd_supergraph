"""
Custom fields.
"""

from django.utils.translation import gettext_lazy as _
from rest_framework.serializers import DictField


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
