import configparser
import json
from pathlib import Path

from core.settings.ini_config import merge_ini_config_with_defaults, merge_dicts
from neotools.serializers import DEFAULTS


PROJECT_DIR = Path(__file__).parent

default_ini_config = {
    "logging": {"level": "INFO"},
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
config_parser.read(PROJECT_DIR / "complex_rest_dtcd_supergraph.conf")
# FIXME option false in config gets converted from 'false' to True
ini_config = merge_ini_config_with_defaults(config_parser, default_ini_config)

# neo4j config
NEO4J = ini_config["neo4j"]

# settings for custom data design
with open(PROJECT_DIR / "serialization.json") as f:
    serialization_conf = json.load(f)
SERIALIZATION_SCHEMA = merge_dicts(serialization_conf, DEFAULTS)

with open(PROJECT_DIR / "exchange.json") as f:
    exchange_conf = json.load(f)
EXCHANGE_SCHEMA = exchange_conf

SCHEMA = merge_dicts(SERIALIZATION_SCHEMA, EXCHANGE_SCHEMA)
