import configparser
from pathlib import Path

import neomodel

# FIXME make this relative? 
import models


PROJECT_DIR = Path(__file__).parent

# FIXME a little ugly - duplication
# main config
config_parser = configparser.ConfigParser(allow_no_value=True)
config_parser.read(PROJECT_DIR / "supergraph.conf")
ini_config = config_parser
# neomodel
# https://neomodel.readthedocs.io/en/latest/configuration.html
protocol = ini_config["neo4j"]["protocol"]
address = ini_config["neo4j"]["address"]
port = ini_config["neo4j"]["port"]
user = ini_config["neo4j"]["user"]
password = ini_config["neo4j"]["password"]
neomodel.config.DATABASE_URL = f"{protocol}://{user}:{password}@{address}:{port}"

# https://neomodel.readthedocs.io/en/latest/module_documentation.html#module-neomodel.core
neomodel.remove_all_labels()
neomodel.install_all_labels()
