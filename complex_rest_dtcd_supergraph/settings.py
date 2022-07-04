import configparser
import json
from pathlib import Path

from core.settings.ini_config import merge_ini_config_with_defaults, merge_dicts


PROJECT_DIR = Path(__file__).parent

default_ini_config = {
    "logging": {
        "level": "INFO",
    },
    "graph": {},
    "workspace": {},
    "neo4j": {
        "uri": "bolt://localhost:7687",
        "user": "neo4j",
        "password": "password",
        "name": "neo4j",
    },
}

# main config
config_parser = configparser.ConfigParser()
config_parser.read(PROJECT_DIR / "supergraph.conf")
# FIXME option false in config gets converted from 'false' to True
ini_config = merge_ini_config_with_defaults(config_parser, default_ini_config)

# neo4j config
NEO4J = ini_config["neo4j"]

# settings for custom data design
SERIALIZATION_SCHEMA = {
    "keys": {
        "parent_key": "key",
        "position": "pos",
    },
    "labels": {
        "array": "Array",
        "attribute": "Attribute",
        "composite": "Composite",
        "data": "Data",
        "entity": "Entity",
        "fragment": "Fragment",
        "item": "Item",
    },
    "types": {
        "contains_item": "CONTAINS_ITEM",
        "contains_entity": "CONTAINS_ENTITY",
        "has_attribute": "HAS_ATTRIBUTE",
        "has_data": "HAS_DATA",
    },
}

EXCHANGE_SCHEMA = {
    "keys": {
        "edges": "edges",
        "groups": "groups",
        "nodes": "nodes",
        "parent_id": "parentID",
        "source_node": "sourceNode",
        "source_port": "sourcePort",
        "target_node": "targetNode",
        "target_port": "targetPort",
        "yfiles_id": "primitiveID",
    },
    "labels": {
        "edge": "Edge",
        "group": "Group",
        "node": "Node",
    },
    "types": {
        "in": "IN",
        "out": "OUT",
    },
}

SCHEMA = merge_dicts(SERIALIZATION_SCHEMA, EXCHANGE_SCHEMA)
