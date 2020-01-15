#!/usr/bin/env python3
"""solve.py: Single model template solver for openCEM"""
__version__ = "0.9.5"
__author__ = "José Zapata"
__copyright__ = "Copyright 2018, ITP Renewables, Australia"
__credits__ = ["José Zapata", "Dylan McConnell", "Navid Hagdadi"]
__license__ = "GPLv3"
__maintainer__ = "José Zapata"
__email__ = "jose.zapata@itpau.com.au"
__status__ = "Development"

import argparse
import datetime
import pickle
import sys
import time

from pyomo.opt import SolverFactory, TerminationCondition

import cemo.utils
from cemo.model import CreateModel, model_options


def check_arg(config_file, parameter):
    '''Parse .dat file for parameters that enable constraints'''
    with open(config_file + '.dat', 'r') as file:
        for line in file:
            if parameter in line:
                return True
        return False


# start the clock on the run
START_TIME = time.time()

# create parser object
PARSER = argparse.ArgumentParser(description="openCEM single model solver")

# Single simulation option using a data command file
PARSER.add_argument("name",
                    help="Specify name of data command file.\n"
                    + " Do not include data command file extension `.dat`",
                    type=str,
                    metavar='NAME')

# Obtain a solver name from command line, default cbc
PARSER.add_argument("--solver",
                    help="Specify solver used by model."
                    + " For Pyomo supported solvers installed in your system ",
                    type=str,
                    metavar='SOLVER',
                    default="cbc")
# Produce only a printout of the instance and exist
PARSER.add_argument("--printonly",
                    help="Produce model.STR.pprint() output and exit."
                    + " STR=all produces entire model output. Debugging only",
                    type=str,
                    metavar='STR')
# Produce a text output of model in Yaml
PARSER.add_argument("--yaml",
                    help="Produce YAML output for the model named NAME.yaml",
                    action="store_true")
# Produce pickle output of instance
PARSER.add_argument("--pickle",
                    help="Produce Pickle of instantiated model object NAME.p",
                    action="store_true")
# Produce a plot
PARSER.add_argument("-p", "--plot",
                    help="Produce a simple plot of model results",
                    action="store_true")
PARSER.add_argument("-u", "--unserved",
                    help="Enforce USE hard constraints",
                    action="store_true")
PARSER.add_argument("-r", "--results",
                    help="Print an abridged model result",
                    action="store_true")
# Include additional output
PARSER.add_argument("-v", "--verbose",
                    help="Print additional output, e.g. solver output",
                    action="store_true")

# parse arguments into args structure
ARGS = PARSER.parse_args()

# Model name comes from command line
MODEL_NAME = ARGS.name

# Parse model options from file
OPTIONS = {'unslim': ARGS.unserved}
for option in model_options()._fields:
    if check_arg(MODEL_NAME, option):
        OPTIONS.update({option: True})
# create cemo model
MODEL = CreateModel(MODEL_NAME, model_options(**OPTIONS)).create_model()

# create a specific instance using file modelName.dat
INSTANCE = MODEL.create_instance(MODEL_NAME + '.dat')

# Produce only a debugging printout of model and then exit
if ARGS.printonly:
    cemo.utils.printonly(INSTANCE, ARGS.printonly)  # print requested keys
    sys.exit(0)  # exit with no error

# declare a solver for the model instance
OPT = SolverFactory(ARGS.solver)

# Use multiple threads for CBC solver (if available)
if ARGS.solver == "cbc":
    OPT.options['threads'] = 4
    OPT.options['ratio'] = 0.0001

# instruct the solver to calculate the solution
print("openCEM solve.py: Runtime %s (pre solver)" %
      str(datetime.timedelta(seconds=(time.time() - START_TIME)))
      )
RESULTS = OPT.solve(INSTANCE, tee=ARGS.verbose, keepfiles=False)
print("openCEM solve.py: Runtime %s (post solver)" %
      str(datetime.timedelta(seconds=(time.time() - START_TIME)))
      )
print("openCEM solve.py: Solver status %s" % RESULTS.solver.status)
if RESULTS.solver.termination_condition == TerminationCondition.infeasible:
    print("openCEM solve.py: Problem infeasible, no solution found.")
    sys.exit(1)
# Produce YAML output of model results
if ARGS.yaml:
    # rescue actual results from instance
    INSTANCE.solutions.store_to(RESULTS)
    # result object to write to json or yaml
    RESULTS.write(filename=MODEL_NAME + '.yaml', format='yaml')

# Produce pickle output of entire instance object
if ARGS.pickle:
    pickle.dump(INSTANCE, open(MODEL_NAME + '.p', 'wb'))

if ARGS.results:
    cemo.utils.printstats(INSTANCE)
# Produce local plot of results
if ARGS.plot:
    cemo.utils.plotresults(INSTANCE)
    cemo.utils.plotcapacity(INSTANCE)
