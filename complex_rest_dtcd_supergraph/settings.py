import configparser
import os
import uuid
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
ini_config = merge_ini_config_with_defaults(config_parser, default_ini_config)

KEYS = SimpleNamespace()
KEYS.edges = "edges"
KEYS.groups = "groups"
KEYS.init_ports = "initPorts"
KEYS.nodes = "nodes"
KEYS.parent_id = "parentID"
KEYS.properties = "properties"
KEYS.source_node = "sourceNode"
KEYS.source_port = "sourcePort"
KEYS.target_node = "targetNode"
KEYS.target_port = "targetPort"
KEYS.value = "value"
KEYS.yfiles_id = "primitiveID"

# neomodel
# https://neomodel.readthedocs.io/en/latest/configuration.html
protocol = ini_config["neo4j"]["protocol"]
address = ini_config["neo4j"]["address"]
port = ini_config["neo4j"]["port"]
user = ini_config["neo4j"]["user"]
password = ini_config["neo4j"]["password"]
neomodel.config.DATABASE_URL = f"{protocol}://{user}:{password}@{address}:{port}"

# DB schema
filename = "default_root_uid.txt"
path = PROJECT_DIR / filename
assert path.exists(), (
    f"Cannot find '{filename}' in this plugin's directory. "
    "Have you forgot to initialize the database with initialize.py?"
)

# graphs configuration

GRAPH_BASE_PATH = ini_config['graph']['base_path']
GRAPH_TMP_PATH = ini_config['graph']['tmp_path']
GRAPH_ID_NAME_MAP_PATH = ini_config['graph']['id_name_map_path']

if not os.path.isdir(GRAPH_BASE_PATH):
    os.mkdir(Path(GRAPH_BASE_PATH))

if not os.path.isdir(GRAPH_TMP_PATH):
    os.mkdir(Path(GRAPH_TMP_PATH))

if not os.path.isdir(GRAPH_ID_NAME_MAP_PATH):
    os.mkdir(Path(GRAPH_ID_NAME_MAP_PATH))

# TODO users can delete default root node, so uid in text file becomes old
# TODO during the testing we reset the database after each test
with open(path) as f:
    try:
        DEFAULT_ROOT_UUID = uuid.UUID(f.read())
    except ValueError:
        raise ValueError(
            "Cannot convert Root uid to UUID. "
            f"Please make sure ID in '{filename}' is a correct UUID."
        )
