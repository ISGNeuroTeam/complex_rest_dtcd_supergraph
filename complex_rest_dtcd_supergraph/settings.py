import configparser
from pathlib import Path

import neomodel

from core.settings.ini_config import merge_ini_config_with_defaults


PROJECT_DIR = Path(__file__).parent

default_ini_config = {
    "logging": {
        "level": "INFO",
    },
    "neo4j": {
        "protocol": "bolt",
        "address": "localhost",
        "port": 7687,
        "user": "neo4j",
        "password": "password",
    },
}

# main config
config_parser = configparser.ConfigParser(allow_no_value=True)
config_parser.read(PROJECT_DIR / "supergraph.conf")
# FIXME option false in config gets converted from 'false' to True
ini_config = merge_ini_config_with_defaults(config_parser, default_ini_config)

# settings for custom data design
SCHEMA = {
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

# neomodel
# https://neomodel.readthedocs.io/en/latest/configuration.html
protocol = ini_config["neo4j"]["protocol"]
address = ini_config["neo4j"]["address"]
port = ini_config["neo4j"]["port"]
user = ini_config["neo4j"]["user"]
password = ini_config["neo4j"]["password"]
neomodel.config.DATABASE_URL = f"{protocol}://{user}:{password}@{address}:{port}"
