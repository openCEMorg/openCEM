# openCEM

Welcome to the repository for the beta version of openCEM

## What is this repository for?

This repository contains the development version of openCEM. You can download and try it in your computer. Please report issues either via:

- Log an issue in the issue tracker (see left pane)
- Email analyticsinfo@itpau.com.au

## Requirements

- A computer with at least 8GB of RAM (16GB or more recommended)
- Windows or Linux OS
- 2GB available in your hard drive (for full result sets)
- An active internet connection for the duration of the run
- Database configuration

## Installation

To run openCEM, you need to install Python 3 and a number of dependencies, a solver and a copy of openCEM. Instructions for all below.

### Python 3

openCEM runs on Python 3, refer to your OS on how to install it in your computer. In addition you will need the following Python packages:

- NumPy
- SciPy
- pandas
- pymysql
- si_prefix
- pytest
- matplotlib
- Pyomo (version 5.6.1 or later)

Note: These can be installed via pip or anaconda. Pyomo needs to be source from `conda-forge`.

### Solver

Thanks to Pyomo, openCEM supports a range of open source and commercial solvers. By default, openCEM uses the COIN-OR Cbc solver. Visit <https://projects.coin-or.org/Cbc> to obtain a copy of Cbc.

Note: [Click here](https://www.coin-or.org/download/binary/OptimizationSuite/COIN-OR-1.7.4-win32-msvc9.exe) to download the recommended windows installer

Note 2: Users experiencing issues with the windows installer can replace the file `cbc.exe` in their systems with that found in [this binary](https://bintray.com/coin-or/download/download_file?file_path=Cbc-2.9-win32-msvc14.zip)

Note 3: Anaconda binaries exist for linux and mac via the `conda-forge` project `coincbc`

Other solvers supported by openCEM:

- cbc (open source, no binary constraints)
- Gurobi (commercial)
- CPLEX (commercial)

### openCEM

Clone the beta version of openCEM from this repository

```bash
git clone https://bitbucket.org/itpanalyitics/opencem-beta.git
```

### Test your Installation

In a python console run the command `pytest` from the openCEM installation directory. If all tests execute correctly and pass, your machine is ready to run openCEM. Here is an example of a successful test message:

```sh
~/opencem $ pytest
................................................................   [100%]
64 passed in 7.38 seconds
```

If the suite is to be run with a solver different than the default, this must be passed as an option to pytest. For example, using GLPK:

```sh
~/opencem $ pytest --solver=glpk
................................................................   [100%]
64 passed in 7.38 seconds
```

## Usage

### Basic usage

openCEM simulates scenarios based on a set of parameters specified in a configuration file. The file `Sample.cfg` as as a template for users to create a variety of scenarios.

To run a configured scenario, type the following command on a console

```sh
$ ./msolve.py Sample.cfg
```

Note: Solvers other than the default must be specified by passing the `--solver` option.

openCEM will process the configuration file and run a simulation. At the end of each simulated year it will print a summary of capacity and dispatch decisions for that period. When finished, openCEM it will save the entire set of results in a JSON file.

### Configuration file

The following explains the purpose of each field in the configuration file. See the file `Sample.cfg` for usage examples and appropriate values. Users can edit files and make multiple copies to manage a range of scenarios. Configuration files uses the Python `configparse` module to import parameters to simulations, therefore observe basic from `configparse` rules for formatting configuration files.

_NOTE_: Results will be written in JSON format using the name of the configuration file as its prefix, e.g. `Sample.cfg.json`

#### `Name`

The field `Name` gives each simulation a descriptive name, which is used as an identifier for simulations.This field must be specified.

#### `Years`

The field `Years` specifies which calendar years on which evaluate capacity and expansion decisions. openCEM will reject any numbers below 2018 and above 2050 due to the absence of data for those years. openCEM will simulate capacity expansions for each of the years declared in the simulation in chronological order. The `Sample.cfg` file suggests 5 year intervals, as a trade-off between resolution against computing time and saved data (about 200MB per simulated year).

#### `nemret`

The field `nemret` specifies, for each year in the `Years` list a renewable energy target (RET) for the NEM as a ratio between 0 and 1 (where 1 corresponds to enforcing 100% renewable target for the NEM). If this field is commented or deleted, no NEM wide RET is enforced in the simulation.

#### `regionret`

The field `regionret` specifies a regional renewable energy target, for each year in the `Years` list and each region in the NEM (1=NSW,2=QLD,3=SA,4=TAS,5=VIC). If the field is omitted no region level RET is enforced. If some regions are omitted, no region level RET is enforced in those regions either. For example, to impose a RET trajectory for VIC and QLD only:

```python
regionret = [
  [5,[0.1, 0.2, 0.3, 0.4]],
  [2,[0.2, 0.3, 0.4, 0.4]]
  ]
```

#### `emitlimit`

The field `emitlimit` specifies a NEM wide emission limits in giga tons (GT) per year of simulation. If the field is commented or omitted, no emission limits are enforced on the simulation.

#### `discountrate`

The field `discountrate` specifies a discount rate for annualised capital cost calculations. Annual capital technology costs are calculated using a fixed charge rate, with lifetimes defined per technology built. This field must be specified.

#### `cost_emit`

The field `cost_emit` specifies a cost penalty for emissions in dollars per kg of total emissions. This field must be specified.

#### `Template`

**For advanced users only. Do not modify**. The `Template` field specifies the scope of the simulation and the sources of data used. The template `ISPNeutral.dat` configures the model to take technology costs, fuel costs and demand projections from the AEMO ISP data and from the NTNDP data for legacy technologies.

#### `custom_costs`

**For advanced users only. Modify with care**. The `custom_costs` field allows users to specify a csv file with overriding values for specific input costs. Values must be specified for each year in the simulation and for the specific cost category, zone and technology. The csv file must contain information in columns as:

```
year, name, zone, tech, value
2025, cost_fuel, 13, 1, 1.3
2030, cost_fuel, 13, 1, 1.31
2035, cost_fuel, 13, 1, 1.31
2040, cost_fuel, 13, 1, 1.32
2045, cost_fuel, 13, 1, 1.33
```

The list of supported costs is:

- `cost_gen_build`, `cost_hyb_build`, `cost_stor_build`
- `cost_fuel`
- `cost_gen_fom`, `cost_stor_fom`, `cost_hyb_fom`
- `cost_gen_vom`, `cost_stor_vom`, `cost_hyb_vom`

Note: Non fuel operating costs are defined per technology only, therefore zone data will be ignored.

#### `cluster`

**For advanced users only. Do not modify**. The field `cluster` enables/disables time slicing dispatch data for a capacity expansion calculation using a combination of reduced dispatch periods. Demand data for each simulated is split into week periods (Mon-Sun 168 hours) and grouped using hierarchical clustering. Capacity calculations are done using a stochastic program (Pyomo PySP).

#### `cluster_sets`

**For advanced users only. Do not modify**. The field `cluster_sets` specifies the number of time sliced periods using for a stochastic program calculation of capacity (See `cluster`).

#### `all_tech_per_zone`

**For advanced users only. Do not modify**. The field `all_tech_per_zone` defines which technologies are enabled for each of the NEM planning zones. See the module `cemo.const` (`cemo/const.py`) for a dictionary reference of zones and technologies in openCEM.
