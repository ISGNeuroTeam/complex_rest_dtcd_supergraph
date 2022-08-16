"""
Helper script to re-install Neo4j constraints and indexes from current
models.
"""

import argparse
import configparser
import sys
from importlib import import_module
from os import path
from pathlib import Path

from neomodel import db, install_all_labels, remove_all_labels


def load_python_module_or_file(name):
    # taken from neomodel source
    # Is a file
    if name.lower().endswith(".py"):
        basedir = path.dirname(path.abspath(name))
        # Add base directory to pythonpath
        sys.path.append(basedir)
        module_name = path.basename(name)[:-3]

    else:  # A module
        # Add current directory to pythonpath
        sys.path.append(path.abspath(path.curdir))

        module_name = name

    if module_name.startswith("."):
        pkg = module_name.split(".")[1]
    else:
        pkg = None

    import_module(module_name, package=pkg)
    print("Loaded {}.".format(name))


def main():
    parser = argparse.ArgumentParser(
        description="""
        Setup indexes and constraints on labels in Neo4j for your neomodel schema.

        Reads database credentials from configuration file.
        """
    )

    parser.add_argument(
        "apps",
        type=str,
        nargs="+",
        help="python modules or files to load schema from.",
    )

    parser.add_argument(
        "config",
        type=Path,
        help="path to configuration file",
    )

    args = parser.parse_args()

    # read database connection settings
    config = configparser.ConfigParser(allow_no_value=True)
    config.read(args.config)
    protocol = config["neo4j"]["protocol"]
    address = config["neo4j"]["address"]
    port = config["neo4j"]["port"]
    user = config["neo4j"]["user"]
    password = config["neo4j"]["password"]
    bolt_url = f"{protocol}://{user}:{password}@{address}:{port}"

    for app in args.apps:
        load_python_module_or_file(app)

    # Connect after to override any code in the module that may set the connection
    print("Connecting to {}\n".format(bolt_url))
    db.set_connection(bolt_url)

    try:
        remove_all_labels()
    except Exception:
        pass

    install_all_labels()


if __name__ == "__main__":
    main()
