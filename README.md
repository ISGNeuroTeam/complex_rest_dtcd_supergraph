# Supergraph plugin

[Complex rest](https://github.com/ISGNeuroTeam/complex_rest/tree/develop) plugin for graph management.

For an introduction check out the [User guide](docs/user-guide.md).

## Installation

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites

1. Deploy [complex rest](https://github.com/ISGNeuroTeam/complex_rest/tree/develop).
2. Install [Neo4j](https://neo4j.com/docs/operations-manual/current/installation/) graph database. We recommend latest patch of version `4.4`, although we support versions `3.5, <=4.4`.
    1. Follow installation instructions [ [Linux](https://neo4j.com/docs/operations-manual/current/installation/linux/) | [Windows](https://neo4j.com/docs/operations-manual/current/installation/windows/) | [Mac](https://neo4j.com/docs/operations-manual/current/installation/osx/) ]. Pay attention to the [required Java version](https://neo4j.com/docs/operations-manual/current/installation/requirements/#deployment-requirements-java); you may need to change system defaults.
    2. Run the service, make sure it is as available at port `7687`.
        ```sh
        systemctl start neo4j
        ```
    3. Set initial password to `password` with the following command:
        ```sh
        neo4j-admin set-initial-password password
        ```
    4. (optional) If you installed *Cypher shell*, you can try to connect to Neo4j to make sure everything is ok:
        ```sh
        cypher-shell -a neo4j://localhost:7687 -u neo4j -p password
        ```

### Deploy from Nexus

For this plugin, you can get the latest build from Nexus.

1. Download archive with the latest build from Nexus.
2. Unpack archive into `complex_rest/plugins` directory.
3. [Re-install constraints and indexes](#re-installing-constraints-and-indexes).
4. Run complex rest server.

### Deploy via Make

1. Clone the Git repository
    ```sh
    git clone https://github.com/ISGNeuroTeam/complex_rest_dtcd_supergraph.git
    ```
2. Run the following from inside the repository root (you'll get the same archive as in Nexus):
    ```sh
    make pack
    ```
3. Unpack archive into `complex_rest/plugins` directory.
4. [Re-install constraints and indexes](#re-installing-constraints-and-indexes).
5. Run complex rest server.

### Deploy manually

1. Clone the Git repository
    ```sh
    git clone https://github.com/ISGNeuroTeam/complex_rest_dtcd_supergraph.git
    ```
2. Enter the folder, copy configuration files from `docs/` to `complex_rest_dtcd_supergraph/` with the following command:
    ```sh
    cd complex_rest_dtcd_supergraph
    cp docs/supergraph.conf.example  complex_rest_dtcd_supergraph/supergraph.conf
    ```
3. Create virtual environment
    ```sh
    python -m venv venv
    ```
4. Activate virtual environment and install the requirements:
    ```sh
    source venv/bin/activate
    pip install -r requirements/production.txt
    ```
5. Make a **symlink** for `./complex_rest_dtcd_supergraph/complex_rest_dtcd_supergraph` in `complex_rest/plugins` directory.
6. [Re-install constraints and indexes](#re-installing-constraints-and-indexes).
7. Run complex rest server.

### Re-installing constraints and indexes

Neo4j provides support for applying [indexes](https://neo4j.com/docs/getting-started/current/graphdb-concepts/#graphdb-indexes) and [constraints](https://neo4j.com/docs/getting-started/current/graphdb-concepts/#graphdb-constraints). To apply these, you need to run `reinstall_labels.py` script inside the plugin's source code directory. Activate virtual environment, navigate to script's parent directory and run it:

```bash
source venv/bin/activate
python reinstall_labels.py
```

## Built With

- [Neo4j](https://neo4j.com/) - Graph data platform.

## Versioning

We use [SemVer](http://semver.org/) for versioning. For the versions available, see the [tags on this repository](https://github.com/your/project/tags). 

## Authors

- Aleksei Tsysin (atsysin@isgneuro.com)

## License

[OT.PLATFORM. License agreement.](LICENSE.md)