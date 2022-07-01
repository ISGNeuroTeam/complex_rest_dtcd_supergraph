"""
Custom DRF serializers.
"""

from rest_framework import serializers

from .fields import GraphField
from .models import Fragment


class FragmentSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True, source="__primaryvalue__")
    name = serializers.CharField(max_length=255)  # TODO value in settings

    def create(self, validated_data) -> Fragment:
        """Construct local fragment instance."""
        return Fragment(**validated_data)

    def update(self, instance, validated_data):
        """Update local fragment instance."""
        instance.name = validated_data["name"]
        return instance

    def save(self, **kwargs) -> Fragment:
        """Create or update local fragment instance."""
        return super().save(**kwargs)


class GraphSerializer(serializers.Serializer):
    graph = GraphField(allow_empty=False)
