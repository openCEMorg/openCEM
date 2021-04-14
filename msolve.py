#!/usr/bin/env python3
"""msolve.py: Multi year solution wrapper openCEM"""
__author__ = "José Zapata"
__copyright__ = "Copyright 2018, ITP Renewables, Australia"
__credits__ = ["José Zapata", "Dylan McConnell", "Navid Hagdadi"]
__license__ = "GPLv3"
__maintainer__ = "José Zapata"
__email__ = "jose.zapata@itpau.com.au"
__status__ = "Development"

import argparse
import datetime
from pathlib import Path
import time

from cemo.multi import SolveTemplate


def valid_file(param):
    """Validates configuration file has the correct extension"""
    ext = Path(param).suffix
    if ext not in (".cfg"):
        raise argparse.ArgumentTypeError("File must have a cfg extension")
    return param


# start the clock on the run
start_time = time.time()

# create parser object
parser = argparse.ArgumentParser(description="openCEM multiyear model solver")

# Multi year simulation option using a configuration file
parser.add_argument(
    "config",
    help="Specify a configuration file for simulation"
    + " Note: Python configuration files named CONFIG.cfg",
    type=valid_file,
    metavar="CONFIG",
)
# Obtain a solver name from command line, default cbc
parser.add_argument(
    "--solver",
    help="Specify solver used by model."
    + " For Pyomo supported solvers installed in your system ",
    type=str,
    metavar="SOLVER",
    default="cbc",
)

# Zip and upload result to custom directory
parser.add_argument(
    "--log",
    help="Request solver logging and traceback information",
    action="store_true",
)

parser.add_argument(
    "-r",
    "--resume",
    help="Resume simulation from last succesfully run year",
    action="store_true",
)

parser.add_argument(
    "-t",
    "--templatetest",
    help="Testing mode where only short dispatch periods are use. Warning, it disables clustering",
    action="store_true",
)

parser.add_argument(
    "-j",
    "--json",
    help="Store results in openCEM v1.0 JSON format",
    action="store_true",
)

# parse arguments into args structure
args = parser.parse_args()

# Read configuration file name from
cfgfile = Path(args.config)

SIM_DIR = Path(cfgfile).parent / Path(cfgfile).stem
if not SIM_DIR.exists():
    SIM_DIR.mkdir()

# create Multi year simulation
X = SolveTemplate(
    cfgfile, solver=args.solver,
    log=args.log,
    wrkdir=SIM_DIR,
    resume=args.resume,
    templatetest=args.templatetest,
    json=args.json
)


# instruct the solver to launch the multi year simulation
print(
    "openCEM msolve.py: Runtime %s (pre solver)"
    % str(datetime.timedelta(seconds=(time.time() - start_time)))
)
X.solve()
print(
    "openCEM msolve.py: Runtime %s (post solver)"
    % str(datetime.timedelta(seconds=(time.time() - start_time)))
)
