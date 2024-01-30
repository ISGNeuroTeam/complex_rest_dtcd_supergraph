# Supergraph plugin

[Complex rest](https://github.com/ISGNeuroTeam/complex_rest/tree/develop) plugin for graph management.  For an introduction check out the [User guide](docs/user-guide.md).

### Prerequisites

1. Deploy [complex rest](https://github.com/ISGNeuroTeam/complex_rest).

### Deploy from GitHub or Nexus

You can get the latest build from either [GitHub releases](https://github.com/ISGNeuroTeam/complex_rest_dtcd_supergraph/releases) page or Nexus - the archives are identical.

1. Download an archive with the latest build.
2. Unpack the archive into `complex_rest/plugins` directory.

### Deploy via Make

If you want to have access to feature branch version, you can build this plugin locally.

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

### Deploy manually

If you are a developer, then follow this section.

1. Clone the Git repository:
    ```sh
    git clone git@github.com:ISGNeuroTeam/complex_rest.git repo
    ```
2. Enter the folder, copy or symlink configuration files from `docs/` to `complex_rest_dtcd_supergraph/` with the following commands:
    ```sh
    cd repo
    cp docs/supergraph.conf  complex_rest_dtcd_supergraph/supergraph.conf
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

## Deployment

For deployment, we need to get a build archive - see the previous section on how to do that. Then:

1. Stop `complex_rest`.
2. Unpack the archive into `complex_rest/plugins` directory.
3. Start `complex_rest`.

## TODO

- Update [User guide](docs/user-guide.md).

## Versioning

We use [SemVer](http://semver.org/) for versioning. For the versions available, see the [tags on this repository](https://github.com/ISGNeuroTeam/complex_rest/tags). 

## Authors

- Aleksei Tsysin (atsysin@isgneuro.com)
- Nikita Serditov (nserditov@isgneuro.com)

## License

[OT.PLATFORM. License agreement.](LICENSE.md)