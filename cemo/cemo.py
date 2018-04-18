# CEMO model structure
from pyomo.environ import AbstractModel, Var, Param, Constraint, Objective, Set
from pyomo.environ import NonNegativeReals
from cemo.rules import con_loadbalance, con_maxcap, con_capfactor
from cemo.rules import obj_cost


def create_model(namestr):
    """Creates an instance of the pyomo definition of CEMO"""
    model = AbstractModel(name=namestr)
    # Sets
    model.R = Set()  # Set of regions
    model.N = Set()  # Set of generation technologies
    model.T = Set()  # Set of dispatch intervals
    model.D = Set()  # Set of representative dispatch periods
    model.Inv = Set()  # Set of investment periods

    # @@ Parameters
    model.CC = Param(model.R, model.N, model.Inv)  # Capital costs
    model.CF = Param(model.R, model.N, model.Inv)  # Fixed operating costs
    model.CV = Param(model.R, model.N, model.Inv)  # Variable operating costs
    model.Cuns = Param()  # cost of unserved power
    model.Csur = Param()  # cost or value if negative, of surplus power

    model.capf = Param(model.R, model.N, model.T,
                       default=1)  # Capacity factors
    model.MaxCap = Param(model.R, model.N)
    model.OpCap = Param(model.R, model.N)  # operating capacity

    model.Ld = Param(model.R, model.T)  # Electrical load

    # @@ Variables
    model.NewCap = Var(model.R, model.N, model.Inv,
                       within=NonNegativeReals)  # New capacity
    model.q = Var(model.R, model.N, model.T,
                  within=NonNegativeReals)  # dispatched power

    model.quns = Var(model.R, model.N, model.T,
                     within=NonNegativeReals)  # unserved power

    model.surplus = Var(model.R, model.N, model.T,
                        within=NonNegativeReals)  # excess power

    # @@ Constraints
    # Load balance
    model.ldbal = Constraint(model.T, rule=con_loadbalance)
    # Dispatch to be within capacity, RE have variable capacity factors
    model.caplim = Constraint(model.R, model.N, model.T, rule=con_capfactor)
    # Limit maximum capacity to be built in each region and each technology
    model.maxcap = Constraint(model.R, model.N, rule=con_maxcap)

    # @@ Objective
    # Minimise capital, variable and fixed costs of system
    model.Obj = Objective(rule=obj_cost)

    return model
