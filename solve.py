# Capacity expansion model and optimiser
# Copyright ITP renewables 2018
# See license for licensiong details
from pyomo.environ import value
from cemo.cemo import create_model
from pyomo.opt import SolverFactory
import matplotlib.pyplot as plt
import numpy as np
import argparse
import pickle

# create parser object
parser = argparse.ArgumentParser()

# Require a name for created model
parser.add_argument("--name",
                    help="Specify name of model. Note: associated files must match this name",
                    type=str,
                    metavar='NAME',
                    required=True)
# Produce a plot
parser.add_argument("--plot",
                    help="Produce a simple plot of model results",
                    action="store_true")
# Produce a text output of model in Yaml
parser.add_argument("--yaml",
                    help="Produce YAML output for the model named NAME.yaml",
                    action="store_true")
parser.add_argument("--pickle",
                    help="Produce Pickle of instantiated model object, named NAME.p",
                    action="store_true")
args = parser.parse_args()

modelName = args.name
# create cemo model
model = create_model(modelName)
# create a specific instance using provided data file
instance = model.create_instance(modelName + '.dat')
# declare a solver for the model instance
opt = SolverFactory("cbc")
# Use multiple threads for CBC solver ()
opt.options['threads'] = 4
# instruct the solver to calculate the solution
results = opt.solve(instance, tee=False, keepfiles=False)

if args.yaml:
    # rescue actual results from instance
    instance.solutions.store_to(results)
    # result object to write to json or yaml
    results.write(filename=modelName + '.yaml', format='yaml')

if args.pickle:
    pickle.dump(instance, open(modelName + '.p', 'wb'))


if args.plot:
    # Process results to plot. This is rather crude but it helps to visualise
    # what is the model doing
    load = np.array([sum(value(instance.Ld[r, t])
                         for r in instance.R) for t in instance.T])
    h = np.array([t for t in instance.T], dtype=np.datetime64)
    qbiomass = np.array([sum(value(instance.q[z, 1, t])
                             for z in instance.Z) for t in instance.T])
    qccgt = np.array([sum(value(instance.q[z, 2, t]) for z in instance.Z)
                      for t in instance.T]) + qbiomass
    qogct = np.array([sum(value(instance.q[z, 8, t]) for z in instance.Z)
                      for t in instance.T]) + qccgt
    qwind = np.array([sum(value(instance.q[z, 12, t]) for z in instance.Z)
                      for t in instance.T]) + qogct
    quns = np.array([sum(value(instance.quns[r, t])
                         for r in instance.R)
                     for t in instance.T]) + qwind
    qsur = np.array([sum(value(instance.surplus[z, n, t])
                         for z in instance.Z for n in instance.TechperZone[z])
                     for t in instance.T]) + load
    fig, ax = plt.subplots()

    ax.plot(h, qbiomass, h, qccgt, h, qogct, h, qwind, h, load)
    ax.fill_between(h, quns, qwind, where=qwind <= quns, facecolor='red')
    ax.fill_between(h, load, qsur, facecolor='blue')
    ax.legend(['Biomass', 'CCGT', 'OCGT', 'WIND',
               'load', 'unserved', 'surplus'])
    fig.autofmt_xdate()
    plt.show(block=True)
