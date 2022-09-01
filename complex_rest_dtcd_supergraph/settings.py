import configparser
import uuid
from pathlib import Path
from types import SimpleNamespace

import neomodel

from core.settings.ini_config import merge_ini_config_with_defaults


PROJECT_DIR = Path(__file__).parent
# see how complex_rest loads the plugins
PLUGIN_NAME = PROJECT_DIR.name

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

# Role Model settings; see role model documentation for more info
ROLE_MODEL_ACTION_NAMES = SimpleNamespace()
# action names for graph operations
ROLE_MODEL_ACTION_NAMES.clear = "clear"
ROLE_MODEL_ACTION_NAMES.read = "read"
ROLE_MODEL_ACTION_NAMES.replace = "replace"

ROLE_MODEL_ACTIONS = {
    # actions for graph operations
    ROLE_MODEL_ACTION_NAMES.clear: {
        "default_rule": True,  # allow or deny True or False, default True,
        "owner_applicability": True,  # default True
    },
    ROLE_MODEL_ACTION_NAMES.read: {
        "default_rule": True,
        "owner_applicability": True,
    },
    ROLE_MODEL_ACTION_NAMES.replace: {
        "default_rule": True,
        "owner_applicability": True,
    },
}
# paths to classes covered by role model management (relative to src dir)
ROLE_MODEL_AUTH_COVERED_CLASSES = [
    "models.Container",
]
ROLE_MODEL_AUTH_COVERED_CLASSES = [
    PLUGIN_NAME + "." + item  # plugin.relpathtoclass
    for item in ROLE_MODEL_AUTH_COVERED_CLASSES
]

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
DEFAULT_ROOT_UUID = uuid.UUID(int=0)
DEFAULT_ROOT_DATA = dict(
    name="Root",
)
