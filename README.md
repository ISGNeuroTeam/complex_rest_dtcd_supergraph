# Supergraph plugin

[Complex rest](https://github.com/ISGNeuroTeam/complex_rest/tree/develop) plugin for graph management.

For an introduction check out the [User Guide](docs/user-guide.md) and [Extra Notes](docs/notes.md) documents, or see the [Roadmap](docs/roadmap.md) to know what to work on.

## Installation

These instructions will get you a copy of the plugin up and running on your local machine for development and testing purposes. See [deployment](#deployment) for notes on how to deploy the plugin on a live system.

### Prerequisites

1. Deploy [complex rest](https://github.com/ISGNeuroTeam/complex_rest).
2. Install [Neo4j](https://neo4j.com/docs/operations-manual/current/installation/) graph database.
    1. Follow installation instructions for your OS [ [Linux](https://neo4j.com/docs/operations-manual/current/installation/linux/) | [Windows](https://neo4j.com/docs/operations-manual/current/installation/windows/) | [Mac](https://neo4j.com/docs/operations-manual/current/installation/osx/) ]. Pay attention to the [required Java version](https://neo4j.com/docs/operations-manual/current/installation/requirements/#deployment-requirements-java); you may need to change system defaults.
    2. [Set initial password](https://neo4j.com/docs/operations-manual/current/configuration/set-initial-password/) to `password` with the following command:
        ```sh
        neo4j-admin set-initial-password password
        ```
        > This must be performed before starting up the database for the first time.
    3. Run the service, make sure it is available on port `7687`:
        ```sh
        systemctl start neo4j
        ```
    4. (optional) If you installed *Cypher shell*, you can try to connect to Neo4j to make sure everything is ok:
        ```sh
        cypher-shell -a neo4j://localhost:7687 -u neo4j -p password
        ```

### Install from GitHub or Nexus

You can get the latest build from either [GitHub releases](https://github.com/ISGNeuroTeam/complex_rest_dtcd_supergraph/releases) page or Nexus - the archives are identical.

1. Download an archive with the latest build.
2. Unpack the archive into `complex_rest/plugins` directory.
3. Run the [initialization script](#initialization-script) to prepare the database.

### Install via Make

If you want to have an access to feature branch version, you can build this plugin locally.

1. Clone the Git repository:
    ```sh
    git clone https://github.com/ISGNeuroTeam/complex_rest_dtcd_supergraph.git repo
    ```
2. Enter the folder and use `Makefile` to build an archive (you'll get the same one as in GitHub/Nexus):
    ```sh
    cd repo
    make pack
    ```
3. Unpack the archive into `complex_rest/plugins` directory.
4. Run the [initialization script](#initialization-script) to prepare the database.

### Install manually

If you are a developer, then follow this section.

1. Clone the Git repository (optionally, into `complex_rest/plugin_dev` folder):
    ```sh
    git clone git@github.com:ISGNeuroTeam/complex_rest.git repo
    ```
2. Enter the folder, copy or symlink configuration files from `docs/` to `complex_rest_dtcd_supergraph/` with the following commands:
    ```sh
    cd repo
    cp docs/supergraph.conf.example  complex_rest_dtcd_supergraph/supergraph.conf
    ```
3. Create a virtual environment:
    ```sh
    python3 -m venv venv
    ```
4. Activate the virtual environment and install the requirements:
    ```sh
    source venv/bin/activate
    pip install -r requirements/local.txt
    ```
5. Create a **symlink** for the source folder in `complex_rest/plugins`:
    ```sh
    cd complex_rest/plugins
    ln -s pathtofolder/repo/complex_rest_dtcd_supergraph
    ```
6. [Re-install constraints and indexes](#re-installing-constraints-and-indexes), [initialize the default `Root` node](#initializing-the-default-root).

## Deployment

For deployment we need to get a build archive - see the previous section on how to do that. Then:

1. Stop `complex_rest`.
2. Unpack the archive into `complex_rest/plugins` directory.
3. Run the [initialization script](#initialization-script) to prepare the database.
4. **TODO** Backup / reset / migrate the database.
5. Start `complex_rest`.

## Running the tests

[Install this plugin manually](#install-manually), then navigate to `complex_rest` root directory, activate project's virtual environment and run:

```sh
python complex_rest/manage.py test \
    plugin_dev/complex_rest_dtcd_supergraph/tests/ \
    --settings="core.settings.test" \
```

> You might need to install base requirements into project's `venv` for this to work.

## Notes

### Re-installing constraints and indexes

Neo4j provides support for applying [indexes](https://neo4j.com/docs/getting-started/current/graphdb-concepts/#graphdb-indexes) and [constraints](https://neo4j.com/docs/getting-started/current/graphdb-concepts/#graphdb-constraints).

To do this, activate plugin's virtual environment and run:

```sh
address="bolt://neo4j:password@localhost:7687"
neomodel_remove_labels --db $address
neomodel_install_labels models --db $address
```

For password and port use values from `supergraph.conf`.

### Initializing the default Root

We need to create the default root node in order to keep backwards compatibility with the API v0.2.0. There is a script just for that!

Activate plugin's virtual environment, navigate to script's parent directory and run:

```sh
python create_default_root.py
```

It will create a single `Root` node and save its `uid` attribute in the file `default_root_uid.txt` inside source code directory.

### Initialization script

There is a helper script `database_init.sh` that prepares the plugin for work when deploying *from build archive*. It combines activation of correct virtual environment, [re-installation of constraints and indexes](#re-installing-constraints-and-indexes) with [default Root creation](#initializing-the-default-root) in one place.

You can run it from anywhere you like:

```sh
./database_init.sh
```

## TODO

- Update [User guide](docs/user-guide.md).
- Resolve `RelationshipClassRedefined` error when trying to test `neomodel` models directly (see `test_managers.py`).
- User-defined properties that were saved before *stay on the node after merge* even if they are missing in new structure and should be deleted (see how `create_or_update` works). We handle it in converter, but this is not nice.
- Resolve possible **clashes** between explicit and user-defined properties on nodes when merging content.
- Migration scripts (`upgrade.v0.v1.sh`) for this plugin.
- Some database queries may be inefficient (`n+1` problems).
- Add Django auth to views.

## Built With

- [Neo4j](https://neo4j.com/) - Graph data platform.

## Versioning

We use [SemVer](http://semver.org/) for versioning. For the versions available, see the [tags on this repository](https://github.com/ISGNeuroTeam/complex_rest/tags). 

## Authors

- Aleksei Tsysin (atsysin@isgneuro.com)

## License

[OT.PLATFORM. License agreement.](LICENSE.md)
