# Capacity expansion model and optimiser
# Copyright ITP renewables 2018
# See license for licensiong details
from pyomo.environ import value
from cemo.cemo import create_model
from pyomo.opt import SolverFactory
import matplotlib.pyplot as plt
import numpy as np

# create cemo model
model = create_model('CEMO')
# create a specific instance using provided data file
instance = model.create_instance('CEMO.dat')
# declare a solver for the model instance
opt = SolverFactory("glpk")
# instruct the solver to calculate the solution
results = opt.solve(instance,)
# rescue actual results from instance
instance.solutions.store_to(results)
# result object to write to json or yaml
results.write(filename='results.yaml', format='yaml')

# Process results to plot. This is rather crude but it helps to visualise
# what is the model doing
load = np.array([sum(value(instance.Ld[r, t])
                     for r in instance.R) for t in instance.T])

h = np.array([t for t in instance.T])
qbrc = np.array([sum(value(instance.q[r, 'BRC', t])
                     for r in instance.R) for t in instance.T])
qbkc = np.array([sum(value(instance.q[r, 'BKC', t]) for r in instance.R)
                 for t in instance.T]) + qbrc
qscc = np.array([sum(value(instance.q[r, 'SCC', t]) for r in instance.R)
                 for t in instance.T]) + qbkc
qhy = np.array([sum(value(instance.q[r, 'HY', t]) for r in instance.R)
                for t in instance.T]) + qscc
qw = np.array([sum(value(instance.q[r, 'W', t]) for r in instance.R)
               for t in instance.T]) + qhy
qpv = np.array([sum(value(instance.q[r, 'PV', t]) for r in instance.R)
                for t in instance.T]) + qw
qcsp = np.array([sum(value(instance.q[r, 'CSP', t]) for r in instance.R)
                 for t in instance.T]) + qpv
quns = np.array([sum(value(instance.quns[r, n, t])
                     for r in instance.R for n in instance.N)
                 for t in instance.T]) + np.minimum(qcsp, load)
qsur = np.array([sum(value(instance.surplus[r, n, t])
                     for r in instance.R for n in instance.N)
                 for t in instance.T]) + load
plt.clf()
plt.plot(h, qbrc, h, qbkc, h, qscc, h, qhy, h,
         qw, h, qpv, h, qcsp, h, load)
plt.fill_between(h, qcsp, quns, where=-1 <= quns - qcsp, facecolor='red')
plt.fill_between(h, load, qsur, facecolor='blue')
plt.legend(['BRC', 'BKC', 'SCC', 'HY', 'W', 'PV',
            'CSP', 'load', 'unserved', 'surplus'])
plt.show(block=True)
