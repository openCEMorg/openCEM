# CEMO model structure
from pyomo.environ import AbstractModel, Var, Param, Constraint, Objective, Set
from pyomo.environ import NonNegativeReals, NonNegativeIntegers, BuildAction
from cemo.rules import con_ldbal, con_maxcap, con_caplim, con_opcap
from cemo.rules import obj_cost, ScanForTechperZone, ScanForZoneperRegion


def create_model(namestr):
    """Creates an instance of the pyomo definition of CEMO"""
    model = AbstractModel(name=namestr)
    # Sets
    model.R = Set()  # Set of NEM regions
    model.Z = Set()  # Set of NTNDP planning zones
    model.ZinR = Set(dimen=2)  # Sparse set of zones per region
    model.ZperR = Set(model.R, within=model.Z, initialize=[])
    model.N = Set()  # Set of generation technologies
    model.T = Set(ordered=True)  # Set of dispatch intervals
    model.D = Set()  # Set of representative dispatch periods
    model.Inv = Set()  # Set of investment periods
    # Set listing technologies avaialable per zone (like a sparsity pattern)
    model.TechinZones = Set(dimen=2)
    # sparse set to index techs available in each zone (used in rules)
    # i.e. TechperZone[i] returns a tuple with the techs in that region
    model.TechperZone = Set(model.Z, within=model.N, initialize=[])

    # @@ Build actions
    # Scan TechinZone and populate TechperZone
    model.TpZ_build = BuildAction(rule=ScanForTechperZone)
    # Scan ZinR and populate ZperR
    model.ZpR_build = BuildAction(rule=ScanForZoneperRegion)

    # @@ Parameters
    model.CC = Param(model.TechinZones, model.Inv)  # Capital costs
    model.CF = Param(model.TechinZones, model.Inv)  # Fixed operating costs
    model.CV = Param(model.TechinZones, model.Inv)  # Variable operating costs
    model.Cuns = Param()  # cost of unserved power
    model.Csur = Param()  # cost or value if negative, of surplus power

    model.capf = Param(model.TechinZones, model.T,
                       default=1)  # Capacity factors
    model.MaxCap = Param(model.TechinZones)
    model.OpCap0 = Param(model.TechinZones)  # operating capacity

    model.Ld = Param(model.R, model.T)  # Electrical load

    # @@ Variables
    model.NewCap = Var(model.TechinZones, model.Inv,
                       within=NonNegativeIntegers)  # New capacity
    model.OpCap = Var(model.TechinZones, model.Inv,
                      within=NonNegativeReals)  # Total capacity for Inv period
    model.q = Var(model.TechinZones, model.T,
                  within=NonNegativeReals)  # dispatched power

    model.quns = Var(model.R, model.T,
                     within=NonNegativeReals)  # unserved power

    model.surplus = Var(model.TechinZones, model.T,
                        within=NonNegativeReals)  # excess power

    # @@ Constraints
    # Load balance
    model.ldbal = Constraint(model.R, model.T, rule=con_ldbal)
    # Dispatch to be within capacity, RE have variable capacity factors
    model.caplim = Constraint(model.TechinZones, model.T, rule=con_caplim)
    # Limit maximum capacity to be built in each region and each technology
    model.maxcap = Constraint(model.TechinZones, model.Inv, rule=con_maxcap)
    # OpCap in existing period is previous OpCap plus NewCap
    model.opcap = Constraint(model.TechinZones, model.Inv, rule=con_opcap)

    # @@ Objective
    # Minimise capital, variable and fixed costs of system
    model.Obj = Objective(rule=obj_cost)

    return model
