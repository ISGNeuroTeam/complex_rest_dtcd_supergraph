import configparser
from pathlib import Path
from types import SimpleNamespace

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

KEYS = SimpleNamespace()
KEYS.edges = "edges"
KEYS.groups = "groups"
KEYS.init_ports = "initPorts"
KEYS.nodes = "nodes"
KEYS.parent_id = "parentID"
KEYS.source_node = "sourceNode"
KEYS.source_port = "sourcePort"
KEYS.target_node = "targetNode"
KEYS.target_port = "targetPort"
KEYS.yfiles_id = "primitiveID"


# neomodel
# https://neomodel.readthedocs.io/en/latest/configuration.html
protocol = ini_config["neo4j"]["protocol"]
address = ini_config["neo4j"]["address"]
port = ini_config["neo4j"]["port"]
user = ini_config["neo4j"]["user"]
password = ini_config["neo4j"]["password"]
neomodel.config.DATABASE_URL = f"{protocol}://{user}:{password}@{address}:{port}"
