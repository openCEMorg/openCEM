#!/usr/bin/env python3
"""solve.py: Single model solver for openCEM"""
__version__ = "0.1.1"
__author__ = "José Zapata"
__copyright__ = "Copyright 2018, ITP Renewables, Australia"
__credits__ = ["José Zapata", "Dylan McConnell", "Navid Hagdadi"]
__license__ = "?GPL"
__maintainer__ = "José Zapata"
__email__ = "jose.zapata@itpau.com.au"
__status__ = "Development"

from cemo.model import create_model
from pyomo.opt import SolverFactory, TerminationCondition
import cemo.utils
import argparse
import pickle
import sys
import time
import datetime

# start the clock on the run
start_time = time.time()

# create parser object
parser = argparse.ArgumentParser(description="openCEM single model solver")

# Single simulation option using a data command file
parser.add_argument("name",
                    help="Specify name of data command file.\n"
                    + " Do not include data command file extension `.dat`",
                    type=str,
                    metavar='NAME')

# Obtain a solver name from command line, default cbc
parser.add_argument("--solver",
                    help="Specify solver used by model."
                    + " For Pyomo supported solvers installed in your system ",
                    type=str,
                    metavar='SOLVER',
                    default="cbc")
# Produce only a printout of the instance and exist
parser.add_argument("--printonly",
                    help="Produce model.STR.pprint() output and exit."
                    + " STR=all produces entire model output. Debugging only",
                    type=str,
                    metavar='STR')
# Produce a text output of model in Yaml
parser.add_argument("--yaml",
                    help="Produce YAML output for the model named NAME.yaml",
                    action="store_true")
# Produce pickle output of instance
parser.add_argument("--pickle",
                    help="Produce Pickle of instantiated model object NAME.p",
                    action="store_true")
# Produce a plot
parser.add_argument("-p", "--plot",
                    help="Produce a simple plot of model results",
                    action="store_true")
parser.add_argument("-u", "--unserved",
                    help="Enforce USE hard constraints",
                    action="store_true")
parser.add_argument("-e", "--emissions",
                    help="Enforce Total emisssions hard constraints",
                    action="store_true")
parser.add_argument("-r", "--results",
                    help="Print an abridged model result",
                    action="store_true")
# Include additional output
parser.add_argument("-v", "--verbose",
                    help="Print additional output, e.g. solver output",
                    action="store_true")

# parse arguments into args structure
args = parser.parse_args()

# Model name comes from command line
modelName = args.name

# create cemo model
# TODO expose nemret and regionrate to args
model = create_model(modelName, unslim=args.unserved, emitlimit=args.emissions)
# create a specific instance using file modelName.dat
try:
    instance = model.create_instance(modelName + '.dat')
except Exception as ex:
    print("openCEM solve.py: ", ex)
    sys.exit(1)  # exit gracefully if file does not exist

# Produce only a debugging printout of model and then exit
if args.printonly:
    cemo.utils.printonly(instance, args.printonly)  # print requested keys
    sys.exit(0)  # exit with no error

# declare a solver for the model instance
opt = SolverFactory(args.solver)

# Use multiple threads for CBC solver (if available)
# TODO pass solver options via command line interface
if args.solver == "cbc":
    opt.options['threads'] = 4
    opt.options['ratio'] = 0.0001

# instruct the solver to calculate the solution
print("openCEM solve.py: Runtime %s (pre solver)" %
      str(datetime.timedelta(seconds=(time.time() - start_time)))
      )
results = opt.solve(instance, tee=args.verbose, keepfiles=False)
print("openCEM solve.py: Runtime %s (post solver)" %
      str(datetime.timedelta(seconds=(time.time() - start_time)))
      )
print("openCEM solve.py: Solver status %s" % results.solver.status)
if results.solver.termination_condition == TerminationCondition.infeasible:
    print("openCEM solve.py: Problem infeasible, no solution found.")
    sys.exit(1)
# Produce YAML output of model results
if args.yaml:
    # rescue actual results from instance
    instance.solutions.store_to(results)
    # result object to write to json or yaml
    results.write(filename=modelName + '.yaml', format='yaml')

# Produce pickle output of entire instance object
if args.pickle:
    pickle.dump(instance, open(modelName + '.p', 'wb'))

if args.results:
    cemo.utils.printstats(instance)
# Produce local plot of results
if args.plot:
    cemo.utils.plotresults(instance)
    cemo.utils.plotcapacity(instance)
