import configparser
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

# TODO users can delete default root node, so uid in text file becomes old
# TODO during the testing we reset the database after each test
with open(path) as f:
    DEFAULT_ROOT_UUID = uuid.UUID(hex=f.read())
