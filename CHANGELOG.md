# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).


## [Unreleased]
### Added
- Serializer with validation for incoming payloads with graph content (IDs & integrity checks).

### Changed
- Logger name changed to `supergraph`.

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