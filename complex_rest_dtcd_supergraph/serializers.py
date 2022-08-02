"""
Custom DRF serializers.
"""

from itertools import chain
from operator import itemgetter
from types import SimpleNamespace

from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from .fields import CustomUUIDFIeld, EdgeField, GroupField, VertexField
from .models import Container, Fragment, Root
from .settings import KEYS


class ContainerSerializer(serializers.Serializer):
    id = CustomUUIDFIeld(read_only=True, source="uid")
    name = serializers.CharField(max_length=255)  # TODO value in settings

    container_class = Container

    def create(self, validated_data):
        """Construct an instance and save it to the database."""

        return self.container_class(**validated_data).save()

    def update(self, instance: container_class, validated_data: dict):
        """Update the instance in the database."""

        instance.name = validated_data["name"]

        return instance.save()

    def save(self, **kwargs) -> container_class:
        """Create or update an instance in the database."""

        return super().save(**kwargs)


class FragmentSerializer(ContainerSerializer):
    container_class = Fragment


class RootSerializer(ContainerSerializer):
    container_class = Root

    fragments = FragmentSerializer(read_only=True, source="fragments.all", many=True)


class ContentSerializer(serializers.Serializer):
    default_error_messages = {
        "does_not_exist": _("An entity with id [{value}] does not exist."),
        "not_unique": _("Data contains non-unique, duplicated IDs."),
        "self_reference": _("A group with id [{value}] has a self-reference."),
    }

    keys = SimpleNamespace(
        id=KEYS.yfiles_id,
        src_node=KEYS.source_node,
        tgt_node=KEYS.target_node,
        src_port=KEYS.source_port,
        tgt_port=KEYS.target_port,
        parent_id=KEYS.parent_id,
        init_ports=KEYS.init_ports,
    )

    nodes = serializers.ListField(child=VertexField(), allow_empty=False)
    edges = serializers.ListField(child=EdgeField())
    groups = serializers.ListField(required=False, child=GroupField())

    # TODO validate uniqueness of all IDs

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
        # unique IDs
        value = self.validate_nodes(value)

        # no self-reference
        for obj in value:
            id_ = obj[self.keys.id]
            parent_id = obj.get(self.keys.parent_id)

            if parent_id == id_:
                self.fail("self_reference", value=id_)

        return value

    def validate(self, data: dict):
        self._validate_references(data)
        self._validate_parent_groups_exist(data)

        return data

    def _validate_references(self, data: dict):
        nodes = data["nodes"]
        edges = data["edges"]

        # for each edge, make sure referred nodes really exist
        node_ids = set(map(itemgetter(self.keys.id), nodes))
        for id_ in chain.from_iterable(
            map(itemgetter(self.keys.src_node, self.keys.tgt_node), edges)
        ):
            if id_ not in node_ids:
                self.fail("does_not_exist", value=id_)

        # for each edge, make sure referred ports really exist
        port_ids = set()
        for node in nodes:
            for port in node.get(self.keys.init_ports, []):
                port_ids.add(port.get(self.keys.id))

        for id_ in chain.from_iterable(
            map(itemgetter(self.keys.src_port, self.keys.tgt_port), edges)
        ):
            if id_ not in port_ids:
                self.fail("does_not_exist", value=id_)

    def _validate_parent_groups_exist(self, data: dict):
        # make sure parent groups exist for vertices and groups
        groups = data.get("groups", [])
        group_ids = set(map(itemgetter(self.keys.id), groups))
        nodes = data["nodes"]

        for obj in chain(groups, nodes):
            parent_id = obj.get(self.keys.parent_id)

            if parent_id is not None and parent_id not in group_ids:
                self.fail("does_not_exist", value=parent_id)


class GraphSerializer(serializers.Serializer):
    graph = ContentSerializer()
