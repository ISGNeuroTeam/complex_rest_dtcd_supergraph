"""
Custom DRF serializers.
"""

from itertools import chain
from operator import itemgetter
from types import SimpleNamespace
from typing import List

from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from .fields import EdgeField, GroupField, VertexField
from .models import Fragment
from .settings import SCHEMA


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


class ContentSerializer(serializers.Serializer):
    default_error_messages = {
        "does_not_exist": _("An entity with id [{value}] does not exist."),
        "not_unique": _("Data contains non-unique, duplicated IDs."),
    }

    keys = SimpleNamespace(
        id=SCHEMA["keys"]["yfiles_id"],
        src_node=SCHEMA["keys"]["source_node"],
        tgt_node=SCHEMA["keys"]["target_node"],
        src_port=SCHEMA["keys"]["source_port"],
        tgt_port=SCHEMA["keys"]["target_port"],
        parent_id=SCHEMA["keys"]["parent_id"],
    )

    nodes = serializers.ListField(child=VertexField(), allow_empty=False)
    edges = serializers.ListField(child=EdgeField())
    groups = serializers.ListField(required=False, child=GroupField())

    def validate_nodes(self, value):
        ids = set(map(itemgetter(self.keys.id), value))

        if len(ids) != len(value):
            self.fail("not_unique")

        return value

    def validate_edges(self, value):
        keys = (
            self.keys.src_node,
            self.keys.tgt_node,
            self.keys.src_port,
            self.keys.tgt_port,
        )
        ids = set(map(itemgetter(*keys), value))

        if len(ids) != len(value):
            self.fail("not_unique")

        return value

    def validate_groups(self, value):
        self.validate_nodes(value)

    def validate(self, data: dict):
        self._validate_references(data)
        self._validate_parent_groups_exist(data)
        return data

    def _validate_references(self, data: dict):
        # for each edge, make sure referred nodes really exist
        nodes = data["nodes"]
        node_ids = set(map(itemgetter(self.keys.id), nodes))
        edges = data["edges"]

        for id_ in chain.from_iterable(
            map(itemgetter(self.keys.src_node, self.keys.tgt_node), edges)
        ):
            if id_ not in node_ids:
                self.fail("does_not_exist", value=id_)

    def _validate_parent_groups_exist(self, data: dict):
        # make sure parent groups exist for vertices and groups
        groups = data.get("groups", [])
        group_ids = set(map(itemgetter(self.keys.id), groups))
        nodes = data["nodes"]

        for obj in chain(groups, nodes):
            parent_id = obj.data.get(self.keys.parent_id)

            if parent_id is not None and parent_id not in group_ids:
                self.fail("does_not_exist", value=parent_id)


class GraphSerializer(serializers.Serializer):
    graph = ContentSerializer()
