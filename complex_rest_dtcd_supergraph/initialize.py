"""
Helper script to initialize Neo4j database for work with this plugin.

Does the following:
1. Reset the database.
2. Create initial Root node and save its UID into separate file.
"""


# FIXME make this relative?
from models import Root


def create_default_root_and_save_uid(data: dict, path) -> Root:
    """Create Root node with the data and write its uid to given file."""

    root = Root(**data).save()

    with open(path, "w") as f:
        f.write(str(root.uid))

    return root


if __name__ == "__main__":
    import configparser
    from pathlib import Path
    import neomodel

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

    # TODO leave as is? migrate?
    # re-set the database
    neomodel.clear_neo4j_database(neomodel.db)

    # create default Root and save its UID
    # FIXME same directory? /var/opt/complex_rest/plugins/supergraph?
    filename = "default_root_uid.txt"

    create_default_root_and_save_uid(
        data={"name": ini_config["schema"]["default_root_name"]},
        path=PROJECT_DIR / filename,
    )
