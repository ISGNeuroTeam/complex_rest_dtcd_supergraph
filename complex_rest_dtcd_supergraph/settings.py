import configparser
import os
import uuid
from pathlib import Path
from types import SimpleNamespace

from core.settings.ini_config import merge_ini_config_with_defaults


PROJECT_DIR = Path(__file__).parent

default_ini_config = {
    "logging": {
        "level": "INFO",
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
