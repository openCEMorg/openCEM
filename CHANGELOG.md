# Changelog

Notable changes to openCEM

## [0.9.1] - 2019-02-12

### Added

- "custom costs" field in config gile to override input costs using a csv file
- Added custom cost template example in test folder
- Added changelog
- Pass options for logging and alternative solvers to `msolve.py`

### Updated

- Scenario template no longer contains sets information or default values for technologies. All default sets and parameters are specified in `const.py`
- Installation instructions (anaconda and Windows 10 troubleshooting)
- Usage instructions
- Unit tests for `multi.py`
- Refactored `model` (formerly core) and `initialiser` modules

### Removed

- Data directory with deprecated files

## [0.9.0] - 2018-12-18

### Added

- Beta release of openCEM
- Installation instructions
- Basic usage instructions
- Sample configuration file
