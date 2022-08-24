# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).


## [Unreleased]
### Added
- Roadmap and notes documents.

### Changed
- User guide update.

## [0.3.3] - 2022-08-18
### Changed
- Rename startup initialization script to `database_init.sh`.

### Fixed
- Correct order of installation instructions for Neo4j.

## [0.3.2] - 2022-08-16
### Added
- Startup initialization script: automatic re-installation of constraints & indexes, default Root initialization.

### Fixed
- Error when removing non-existent labels in `neomodel_remove_labels`.

## [0.3.1] - 2022-08-10
### Fixed
- Add an endpoint for default root graph management.
- Fix bug with content deletion in root graph view `delete()` method. Now it correctly leaves fragments intact.

## [0.3.0] - 2022-08-10
### Added
- Support for *root* management.
- Default root initialization to keep backward compatibility with older API.

### Changed
- Switched to `neomodel` and `neo4j-driver`.
- Architecture rework.
- Endpoints for fragment management.
- Now we keep suffix `complex_rest_dtcd_` from plugin folder when making final archive, again.

### Deprecated
- User guide is no longer up-to-date. Will update in a future release.

### Removed
- `py2neo` dependency and supporting scripts.
- Deprecated support for recursive serialization of nested structures.

## [0.2.0] - 2022-07-22
### Added
- Support for *groups* in graph data.
- Serializer with validation for incoming payloads with graph content (IDs & integrity checks).

### Changed
- Logger name changed to `supergraph`.
- Support for Neo4j v3.5.

## [0.1.3] - 2022-07-01
### Changed
- Name of the source folder with code is now `complex_rest_dtcd_supergraph`, again.
- Now we remove suffix `complex_rest_dtcd_` from plugin folder when making final archive.
    > We do this to simplify URL management - see how `complex_rest` uses plugin folder names. 

## [0.1.2] - 2022-06-30
### Changed
- Name of the source folder with code is now `dtcd_supergraph`.

### Fixed
- Bug in branch generation on Jenkins.
- Symlink copy problems on Jenkins.

## [0.1.1] - 2022-06-27
### Added
- Script for fixing py2neo bug.

### Fixed
- Typo / bug in requirements files.
- Freeze package versions in requirements files.

## [0.1.0] - 2022-06-21
Initialized from `dtcd_server` plugin repository.

### Added
- Fragment management and full support for graph-related operations via Neo4j.
- OpenAPI documentation for endpoints (manual).

### Changed
- Simplify general layout of source code folder.
- Incorporate new version of `neo-tools=0.2.0`.
- Split requirements into multiple files.

### Removed
- Workspace-related functionality.
