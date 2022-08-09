# Supergraph plugin

[Complex rest](https://github.com/ISGNeuroTeam/complex_rest/tree/develop) plugin for graph management.

For an introduction check out the [User guide](docs/user-guide.md).

## Installation

These instructions will get you a copy of the plugin up and running on your local machine for development and testing purposes. See [deployment](#deployment) for notes on how to deploy the plugin on a live system.

### Prerequisites

1. Deploy [complex rest](https://github.com/ISGNeuroTeam/complex_rest).
2. Install [Neo4j](https://neo4j.com/docs/operations-manual/current/installation/) graph database.
    1. Follow installation instructions [ [Linux](https://neo4j.com/docs/operations-manual/current/installation/linux/) | [Windows](https://neo4j.com/docs/operations-manual/current/installation/windows/) | [Mac](https://neo4j.com/docs/operations-manual/current/installation/osx/) ]. Pay attention to the [required Java version](https://neo4j.com/docs/operations-manual/current/installation/requirements/#deployment-requirements-java); you may need to change system defaults.
    2. Run the service, make sure it is as available on port `7687`.
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

### Deploy from GitHub or Nexus

For this plugin, you can get the latest build from either [GitHub release](https://github.com/ISGNeuroTeam/complex_rest_dtcd_supergraph/releases) or Nexus (archives are identical).

1. Download an archive with the latest build.
2. Unpack the archive into `complex_rest/plugins` directory.
3. [Re-install constraints and indexes](#re-installing-constraints-and-indexes).

### Deploy via Make

If you don't have an access to Nexus, you can build this plugin locally.

1. Clone the Git repository:
    ```sh
    git clone https://github.com/ISGNeuroTeam/complex_rest_dtcd_supergraph.git
    ```
2. Use `Makefile` to build an archive (you'll get the same one as in GitHub/Nexus):
    ```sh
    make pack
    ```
3. Unpack the archive into `complex_rest/plugins` directory.
4. [Re-install constraints and indexes](#re-installing-constraints-and-indexes).

### Deploy manually

If you are a developer, then follow this section.

1. Clone the Git repository:
    ```sh
    git clone git@github.com:ISGNeuroTeam/complex_rest.git
    ```
2. Enter the folder, copy or symlink configuration files from `docs/` to `complex_rest_dtcd_supergraph/` with the following command:
    ```sh
    cd complex_rest_dtcd_supergraph
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
5. Make a **symlink** for `./complex_rest_dtcd_supergraph/complex_rest_dtcd_supergraph` in `complex_rest/plugins` directory.
6. [Re-install constraints and indexes](#re-installing-constraints-and-indexes).

## Deployment

For deployment we need to get a build archive (see the previous section). Then:

1. Stop `complex_rest`.
2. Unpack the archive into `complex_rest/plugins` directory.
3. [Re-install constraints and indexes](#re-installing-constraints-and-indexes).
4. **TODO** Backup / re-set / migrate the database.
5. Start `complex_rest`.

## Notes

### Re-installing constraints and indexes

Neo4j provides support for applying [indexes](https://neo4j.com/docs/getting-started/current/graphdb-concepts/#graphdb-indexes) and [constraints](https://neo4j.com/docs/getting-started/current/graphdb-concepts/#graphdb-constraints). To apply these, you need to run `reinstall_labels.py` script inside the plugin's source code directory. Activate virtual environment, navigate to script's parent directory and run it:

```bash
source venv/bin/activate
python reinstall_labels.py
```

## Built With

- [Neo4j](https://neo4j.com/) - Graph data platform.

## Versioning

We use [SemVer](http://semver.org/) for versioning. For the versions available, see the [tags on this repository](https://github.com/ISGNeuroTeam/complex_rest/tags). 

## Authors

- Aleksei Tsysin (atsysin@isgneuro.com)

## License

[OT.PLATFORM. License agreement.](LICENSE.md)