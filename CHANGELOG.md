# Changelog

Notable changes to openCEM

## [0.9.4](https://github.com/CEMOsuite/openCEM/tree/0.9.4) - UNRELEASED

### Added

*   [Requirements.txt](./Requirements.txt) added
*   [Docker](https://docker.com) support added
*   Refactored transmission links to work between zones instead of between regions.
*   Added intercon_cap_new and intercon_cap_op to handle existing and new transmission capacity
*   Added scaling factors to proportion regional demand to zones, according to ZONE_DEMAND_PCT in `cemo.const`
*   New constraint limits the total amount of energy generated NEM wide for a technology. This is employed in openCEM to limit biomass generation to a limit based on waste availability to fuel.
*   Operating reserve constraint ensures a minimum amount of spare capacity from dispatchable generators, storage and hybrids is available at each hour.
*   Resume modifier for `msolve`. Intermediate files are now always saved and simulations can be restarted from the last successful year contained in the temporary directory.

### Updated
*   Updated unit tests to conform to code changes
*   Pylint and pycodestyle updates
*   Updated JSON output structure to capture additional decision variables
*   Bug fixes to JSON output data (including those that affect result visualisations)

### Removed
*   Constraints that limit capacity factors per zone and per technology have been deprecated.

## [0.9.3](https://github.com/CEMOsuite/openCEM/tree/0.9.3) - 2019-04-04

### Added

*   TBA

### Updated

*   TBA

### Removed

*   TBA

## [0.9.2](https://github.com/CEMOsuite/openCEM/tree/0.9.2) - 2019-03-31

### Added

*   Linearised unit commitment constraints for less flexible generator
    technologies
*   Minimum dispatchable constraints
*   Minimum renewable dispatchable constraints
*   Carbon price is now a pathway instead of a single value

### Updated

*   Redirected to new standard database schema
*   Default values for technologies
*   Unit tests and coverage

### Removed

*   Bugs and pylint warnings

## [0.9.1](https://github.com/CEMOsuite/openCEM/tree/0.9.1) - 2019-02-12

### Added

*   "custom costs" field in config gile to override input costs using a csv file
*   Added custom cost template example in test folder
*   Added changelog
*   Pass options for logging and alternative solvers to `msolve.py`

### Updated

*   Scenario template no longer contains sets information or default values for
    technologies. All default sets and parameters are specified in `const.py`
*   Installation instructions (anaconda and Windows 10 troubleshooting)
*   Usage instructions
*   Unit tests for `multi.py`
*   Refactored `model` (formerly core) and `initialiser` modules

### Removed

*   Data directory with deprecated files

## [0.9.0](https://github.com/CEMOsuite/openCEM/tree/0.9.0) - 2018-12-18

### Added

*   Beta release of openCEM
*   Installation instructions
*   Basic usage instructions
*   Sample configuration file
