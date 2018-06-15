# Module to host all the rules for the constraints in the abstract model
from pyomo.environ import summation


def ScanForTechperZone(model):
    for (i, j) in model.TechinZones:
        model.TechperZone[i].add(j)


def ScanForZoneperRegion(model):
    for (i, j) in model.ZinR:
        model.ZperR[i].add(j)


def con_ldbal(model, r, t):
    """Provides a rule defining a load balance constraint for the model"""
    return sum(model.q[z, n, t] for z in model.ZperR[r]
               for n in model.TechperZone[z])\
        + model.quns[r, t]\
        == model.Ld[r, t]\
        + sum(model.surplus[z, n, t]
              for z in model.ZperR[r] for n in model.TechperZone[z])


def con_maxcap(model, z, n, i):  # z and n come both from TechinZones
    return model.OpCap[z, n, i] <= model.MaxCap[z, n]


def con_caplim(model, z, n, t):  # z and n come both from TechinZones
    return model.q[z, n, t] + model.surplus[z, n, t]\
        <= model.capf[z, n, t] * model.OpCap[z, n, 2020]


def con_opcap(model, z, n, i):  # z and n come both from TechinZones
    if i == 2020:
        return model.OpCap[z, n, i] == model.OpCap0[z, n]\
            + model.NewCap[z, n, i]
    else:
        return model.OpCap[z, n, i] == model.OpCap[z, n, i - 1]\
            + model.NewCap[z, n, i]


def obj_cost(model):
    capital = summation(model.CC, model.NewCap)
    fixed = summation(model.CF, model.OpCap)
    unserved = model.Cuns * sum(model.quns[r, t]
                                for r in model.R
                                for t in model.T)
    operating = sum(model.CV[z, n, 2020] * model.q[z, n, t]
                    for z in model.Z
                    for n in model.TechperZone[z]
                    for t in model.T)
    surplus = model.Csur * sum(model.surplus[z, n, t]
                               for z in model.Z
                               for n in model.TechperZone[z]
                               for t in model.T)

    return capital + fixed + unserved + operating + surplus
