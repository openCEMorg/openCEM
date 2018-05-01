# Module to host all the rules for the constraints in the abstract model
from pyomo.environ import summation


def con_ldbal(model, t):
    """Provides a rule defining a load balance constraint for the model"""
    return sum(model.q[r, n, t] for r in model.R for n in model.N)\
        + sum(model.quns[r, n, t] for r in model.R for n in model.N)\
        == sum(model.Ld[r, t] for r in model.R)\
        + sum(model.surplus[r, n, t] for r in model.R for n in model.N)


def con_maxcap(model, r, n, i):
    return model.OpCap[r, n, i] <= model.MaxCap[r, n]


def con_caplim(model, r, n, t):
    return model.q[r, n, t] + model.surplus[r, n, t]\
        <= model.capf[r, n, t] * model.OpCap[r, n, 2020]


def con_opcap(model, r, n, i):
    if i == 2020:
        return model.OpCap[r, n, i] == model.OpCap0[r, n]\
            + model.NewCap[r, n, i]
    else:
        return model.OpCap[r, n, i] == model.OpCap[r, n, i - 1]\
            + model.NewCap[r, n, i]


def obj_cost(model):
    capital = summation(model.CC, model.NewCap)
    fixed = summation(model.CF, model.OpCap)
    unserved = model.Cuns * sum(model.quns[r, n, t]
                                for r in model.R for n in model.N for t in model.T)
    operating = sum(model.CV[r, n, 2020] * model.q[r, n, t]
                    for r in model.R for n in model.N for t in model.T)
    surplus = model.Csur * sum(model.surplus[r, n, t]
                               for r in model.R for n in model.N for t in model.T)

    return capital + fixed + unserved + operating + surplus
