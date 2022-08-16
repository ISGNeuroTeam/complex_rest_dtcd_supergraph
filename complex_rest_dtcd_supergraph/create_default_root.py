"""
Helper script creates the initial Root node and saves its UID into a 
file "default_root_uid.txt".
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
    bolt_url = f"{protocol}://{user}:{password}@{address}:{port}"

    # Connect after to override any code in the module that may set the connection
    print("Connecting to {}\n".format(bolt_url))
    neomodel.db.set_connection(bolt_url)

    # create default Root and save its UID
    # FIXME same directory? /var/opt/complex_rest/plugins/supergraph?
    filename = "default_root_uid.txt"

    root = create_default_root_and_save_uid(
        data={"name": ini_config["schema"]["default_root_name"]},
        path=PROJECT_DIR / filename,
    )
    print(f"Created {root} and saved its uid to {filename}.")
