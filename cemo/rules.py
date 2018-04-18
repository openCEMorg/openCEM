# Module to host all the rules for the constraints in the abstract model
from pyomo.environ import summation


def con_loadbalance(model, t):
    """Provides a rule defining a load balance constraint for the model"""
    return sum(model.q[r, n, t] for r in model.R for n in model.N)\
        + sum(model.quns[r, n, t] for r in model.R for n in model.N)\
        == sum(model.Ld[r, t] for r in model.R)\
        + sum(model.surplus[r, n, t] for r in model.R for n in model.N)


def con_maxcap(model, r, n):
    return model.NewCap[r, n, 2020] <= model.MaxCap[r, n]


def con_capfactor(model, r, n, t):
    return model.q[r, n, t] + model.surplus[r, n, t]\
        <= model.capf[r, n, t] * (model.NewCap[r, n, 2020] + model.OpCap[r, n])


def obj_cost(model):
    capital = summation(model.CC, model.NewCap)
    fixed = summation(model.CF, model.NewCap)
    unserved = model.Cuns * sum(model.quns[r, n, t]
                       for r in model.R for n in model.N for t in model.T)
    operating = sum(model.CV[r, n, 2020] * model.q[r, n, t]
                    for r in model.R for n in model.N for t in model.T)
    surplus = model.Cuns * sum(model.surplus[r, n, t]
                       for r in model.R for n in model.N for t in model.T)

    return capital + fixed + unserved + operating + surplus
