# Supergraph plugin

[Complex rest](https://github.com/ISGNeuroTeam/complex_rest/tree/develop) plugin for graph management.

## Getting Started

> **WARNING**: `py2neo` library has a *bug* [[Issue 942](https://github.com/py2neo-org/py2neo/issues/942)]. Depending on deployment option, you might have to run a fixing script on your local machine. Follow [*Fixing `py2neo`* section](#fixing-py2neo).

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites

1. Deploy [complex rest](https://github.com/ISGNeuroTeam/complex_rest/tree/develop).
2. Install [Neo4j](https://neo4j.com/docs/operations-manual/current/installation/) graph database.
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
3. Run complex rest server.

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
4. Run complex rest server.

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
4. Activate virtual environment and install the requirements (you should have access to *Nexus*):
    ```sh
    source venv/bin/activate
    pip install -r requirements/production.txt
    ```
5. [Fix `py2neo`](#fixing-py2neo).
    ```sh
    python docs/fix_py2neo.py venv/lib/python3.9
    python docs/fix_py2neo.py venv/lib64/python3.9
    ```
6. Make a **symlink** for `./complex_rest_dtcd_supergraph/complex_rest_dtcd_supergraph` in `complex_rest/plugins` directory.
7. Run complex rest server.

### Fixing `py2neo`

In order to fix the bug you need to update a file in your locally installed `py2neo` library.

You are looking for a [line 691](https://github.com/py2neo-org/py2neo/blob/master/py2neo/data.py#L691) in `venv/lib/python3.9/site-packages/py2neo/data.py` file. We must change it to the following (note **8 spaces** at the beginning of the line):
```python
        if self.graph and self.identity is not None:
```

For that we have a helper Python script at `docs/fix_py2neo.py`. See documentation with
```sh
python docs/fix_py2neo.py -h
```

## Built With

- [Neo4j](https://neo4j.com/) - Graph data platform.


## Versioning

We use [SemVer](http://semver.org/) for versioning. For the versions available, see the [tags on this repository](https://github.com/your/project/tags). 

## Authors

- Aleksei Tsysin (atsysin@isgneuro.com)


## License

[OT.PLATFORM. License agreement.](LICENSE.md)