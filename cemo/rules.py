# Module to host all the rules for the constraints in the abstract model
import calendar

from pyomo.environ import Constraint

import cemo.const


def init_AdjustYearFactor(model):
    ystr = model.t.first()
    year = int(ystr[:4])
    if calendar.isleap(year):
        hours = 8784
    else:
        hours = 8760
    return hours / len(model.t)


# TODO is fuel price per zone too?
def init_default_fuel_price(model, z, n):
    return cemo.const.DEFAULT_FUEL_PRICE.get(n, 100.0)


def init_default_heat_rate(model, zone, tech):
    return cemo.const.DEFAULT_HEAT_RATE.get(tech, 15.0)


def init_default_fuel_emit_rate(model, tech):
    return cemo.const.DEFAULT_FUEL_EMIT_RATE.get(tech, 800)


def init_cost_retire(model, tech):
    return cemo.const.DEFAULT_RETIREMENT_COST.get(tech, 60000.0)


def init_default_lifetime(model, tech):
    return cemo.const.DEFAULT_TECH_LIFETIME.get(tech, 30.0)


def init_gen_build_limit(model, zone, tech):
    return cemo.const.DEFAULT_BUILD_LIMIT.get(zone).get(tech, 100000)


def init_fcr(model, tech):
    return model.all_tech_discount_rate / (
        (model.all_tech_discount_rate + 1)**model.all_tech_lifetime[tech] -
        1) + model.all_tech_discount_rate


def init_cap_factor(model, zone, tech, time):
    return cemo.const.DEFAULT_CAP_FACTOR.get(tech, 0)


def init_max_hydro(model, zone):
    return cemo.const.DEFAULT_HYDRO_MWH_MAX.get(zone, 0)


def ScanForTechperZone(model):
    for (i, j) in model.gen_tech_in_zones:
        model.gen_tech_per_zone[i].add(j)
    for (i, j) in model.retire_gen_tech_in_zones:
        model.retire_gen_tech_per_zone[i].add(j)
    for (i, j) in model.fuel_gen_tech_in_zones:
        model.fuel_gen_tech_per_zone[i].add(j)
    for (i, j) in model.re_gen_tech_in_zones:
        model.re_gen_tech_per_zone[i].add(j)


def ScanForStorageperZone(model):
    for (i, j) in model.stor_tech_in_zones:
        model.stor_tech_per_zone[i].add(j)


def ScanForHybridperZone(model):
    for (i, j) in model.hyb_tech_in_zones:
        model.hyb_tech_per_zone[i].add(j)


def ScanForZoneperRegion(model):
    for (i, j) in model.zones_in_regions:
        model.zones_per_region[i].add(j)


def ScanForTransLineperRegion(model):
    for (i, j) in model.region_intercons:
        model.intercon_per_region[i].add(j)


def emissions(model, r):
    return sum(model.fuel_emit_rate[n] * model.gen_disp[z, n, t]
               for z in model.zones_per_region[r]
               for n in model.fuel_gen_tech_per_zone[z] for t in model.t)


def dispatch(model, r):
    return sum(model.gen_disp[z, n, t]
               for z in model.zones_per_region[r]
               for n in model.gen_tech_per_zone[z]
               for t in model.t)\
        + sum(model.stor_disp[z, s, t]
              for z in model.zones_per_region[r]
              for s in model.stor_tech_per_zone[z]
              for t in model.t)\
        + sum(model.hyb_disp[z, h, t]
              for z in model.zones_per_region[r]
              for h in model.hyb_tech_per_zone[z]
              for t in model.t)


def con_nem_wide_ret(model):
    return sum(model.gen_disp[z, n, t]
               for r in model.regions
               for z in model.zones_per_region[r]
               for n in model.re_gen_tech_per_zone[z]
               for t in model.t
               )\
        + sum(model.hyb_disp[z, h, t]
              for r in model.regions
              for z in model.zones_per_region[r]
              for h in model.hyb_tech_per_zone[z]
              for t in model.t
              )\
        >= model.nem_ret_ratio * (
        sum(model.gen_disp[z, n, t]
            for r in model.regions
            for z in model.zones_per_region[r]
            for n in model.gen_tech_per_zone[z]
            for t in model.t
            )
        + sum(model.hyb_disp[z, h, t]
              for r in model.regions
              for z in model.zones_per_region[r]
              for h in model.hyb_tech_per_zone[z]
              for t in model.t
              )
    )


def con_region_ret(model, r):
    return sum(model.gen_disp[z, n, t]
               for z in model.zones_per_region[r]
               for n in model.re_gen_tech_per_zone[z]
               for t in model.t
               )\
        + sum(model.hyb_disp[z, h, t]
              for z in model.zones_per_region[r]
              for h in model.hyb_tech_per_zone[z]
              for t in model.t
              )\
        >= model.region_ret_ratio[r] * (
        sum(model.gen_disp[z, n, t]
            for z in model.zones_per_region[r]
            for n in model.gen_tech_per_zone[z]
            for t in model.t
            )
        + sum(model.hyb_disp[z, h, t]
              for z in model.zones_per_region[r]
              for h in model.hyb_tech_per_zone[z]
              for t in model.t
              )
    )


def con_maxmhw(model, z, n):
    if n == 18:  # hydro only
        return sum(model.gen_disp[z, n, t] for t in model.t)\
                <= model.hydro_gen_mwh_limit[z] / model.year_correction_factor
    return Constraint.Skip


def con_maxtrans(model, r, p, t):
    return model.intercon_disp[r, p, t] <= model.intercon_trans_limit[r, p]


def con_chargelim(model, z, s, t):
    return model.stor_charge[z, s, t] <= model.stor_cap_op[z, s]


def con_dischargelim(model, z, s, t):
    return model.stor_disp[z, s, t] <= model.stor_cap_op[z, s]


def con_maxcharge(model, z, s, t):
    return model.stor_level[z, s, t] \
        <= model.stor_cap_op[z, s] * model.stor_charge_hours[s]


def con_storcharge(model, z, s, t):
    if t == model.t.first():
        return model.stor_level[z, s, t] \
            == model.stor_level[z, s, model.t.last()]\
            - model.stor_disp[z, s, t] + \
            model.stor_rt_eff[s] * model.stor_charge[z, s, t]

    return model.stor_level[z, s, t] \
        == model.stor_level[z, s, model.t.prev(t)] \
        - model.stor_disp[z, s, t] + \
        model.stor_rt_eff[s] * model.stor_charge[z, s, t]


def con_hybcharge(model, z, h, t):
    if t == model.t.first():
        return model.hyb_level[z, h, t] \
            == model.hyb_level[z, h, model.t.last()]\
            - model.hyb_disp[z, h, t] \
            + model.hyb_charge[z, h, t]

    return model.hyb_level[z, h, t] \
        == model.hyb_level[z, h, model.t.prev(t)] \
        - model.hyb_disp[z, h, t] \
        + model.hyb_charge[z, h, t]


def con_chargelimhy(model, z, h, t):
    return model.hyb_charge[z, h, t] \
        <= model.hyb_col_mult[h] * model.hyb_cap_factor[z, h, t] * model.hyb_cap_op[z, h]


def con_dischargelimhy(model, z, h, t):
    return model.hyb_disp[z, h, t] <= model.hyb_cap_op[z, h]


def con_maxchargehy(model, z, h, t):
    return model.hyb_level[z, h, t] \
        <= model.hyb_cap_op[z, h] * model.hyb_charge_hours[h]


def con_ldbal(model, r, t):
    """Provides a rule defining a load balance constraint for the model"""
    return sum(model.gen_disp[z, n, t] for z in model.zones_per_region[r]
               for n in model.gen_tech_per_zone[z])\
        + sum(model.hyb_disp[z, h, t] for z in model.zones_per_region[r]
              for h in model.hyb_tech_per_zone[z])\
        + model.unserved[r, t]\
        + sum(model.intercon_disp[p, r, t] for p in model.intercon_per_region[r])\
        + sum(model.stor_disp[z, s, t]
              for z in model.zones_per_region[r] for s in model.stor_tech_per_zone[z])\
        == model.region_net_demand[r, t]\
        + sum((1 + model.intercon_prop_factor[r, p]) * model.intercon_disp[r, p, t]
              for p in model.intercon_per_region[r])\
        + sum(model.stor_charge[z, s, t]
              for z in model.zones_per_region[r] for s in model.stor_tech_per_zone[z])\
        + model.surplus[r, t]


def con_maxcap(model, z, n):  # z and n come both from TechinZones
    return model.gen_cap_op[z, n] <= model.gen_build_limit[z, n]


def con_caplim(model, z, n, t):  # z and n come both from TechinZones
    return model.gen_disp[z, n, t] \
        <= model.gen_cap_factor[z, n, t] * model.gen_cap_op[z, n]


def con_emissions(model):
    '''Emission constraint for the NEM in GT/y for total emissions'''
    return model.year_correction_factor * sum(
        emissions(model, r)
        for r in model.regions) <= 1e9 * model.nem_year_emit_limit


def con_slackretire(model, z, n):
    return model.gen_cap_initial[z, n] - model.ret_gen_cap_exo[
        z, n] + model.gen_cap_ret_neg[z, n] >= 0


def con_opcap(model, z, n):  # z and n come both from TechinZones

    if n in model.nobuild_gen_tech:
        if n in model.retire_gen_tech:
            return model.gen_cap_op[z, n] == model.gen_cap_initial[z, n] \
                + model.gen_cap_exo[z, n]\
                - model.gen_cap_ret[z, n] - \
                (model.ret_gen_cap_exo[z, n] - model.gen_cap_ret_neg[z, n])
        else:
            return model.gen_cap_op[z, n] == model.gen_cap_initial[z, n] \
                + model.gen_cap_exo[z, n]

    else:
        if n in model.retire_gen_tech:
            return model.gen_cap_op[z, n] == model.gen_cap_initial[z, n] \
                + model.gen_cap_exo[z, n]\
                + model.gen_cap_new[z, n]\
                - model.gen_cap_ret[z, n] - \
                (model.ret_gen_cap_exo[z, n] - model.gen_cap_ret_neg[z, n])
        else:
            return model.gen_cap_op[z, n] == model.gen_cap_initial[z, n]\
                + model.gen_cap_exo[z, n]\
                + model.gen_cap_new[z, n]


def con_stcap(model, z, s):  # z and n come both from TechinZones
    if s in model.nobuild_gen_tech:
        return model.stor_cap_op[z, s] == model.stor_cap_initial[z, s] \
            + model.stor_cap_exo[z, s]
    else:
        return model.stor_cap_op[z, s] == model.stor_cap_initial[z, s]\
            + model.stor_cap_exo[z, s]\
            + model.stor_cap_new[z, s]

    if s in model.nobuild_gen_tech:
        if s in model.retire_gen_tech:
            return model.gen_cap_op[z, s] == model.gen_cap_initial[z, s] \
                + model.gen_cap_exo[z, s]\
                - model.gen_cap_ret[z, s] - \
                (model.ret_gen_cap_exo[z, s] - model.gen_cap_ret_neg[z, s])
        else:
            return model.gen_cap_op[z, s] == model.gen_cap_initial[z, s] \
                + model.gen_cap_exo[z, s]


def con_hycap(model, z, h):  # z and n come both from TechinZones
    if h in model.nobuild_gen_tech:
        return model.hyb_cap_op[z, h] == model.hyb_cap_initial[z, h] \
            + model.hyb_cap_exo[z, h]
    else:
        return model.hyb_cap_op[z, h] == model.hyb_cap_initial[z, h]\
            + model.hyb_cap_exo[z, h]\
            + model.hyb_cap_new[z, h]


# IDEA generate set as to reduce delta variables
def con_ramp_up(model, z, n, t):
    if cemo.const.DEFAULT_GEN_RAMP_PENALTY.get(n) is not None:
        if t == model.t.first():
            # cemo.const.DEFAULT_GEN_RAMP_RATE.get(n)
            return model.gen_disp[z, n, t] - model.gen_disp[
                z, n, model.t.last()] <= model.ramp_up_delta[z, n, t]
        # cemo.const.DEFAULT_GEN_RAMP_RATE.get(n)
        return model.gen_disp[z, n, t] - model.gen_disp[
            z, n, model.t.prev(t)] <= model.ramp_up_delta[z, n, t]
    return Constraint.Skip


def con_ramp_down(model, z, n, t):
    if cemo.const.DEFAULT_GEN_RAMP_PENALTY.get(n) is not None:
        if t == model.t.first():
            # cemo.const.DEFAULT_GEN_RAMP_RATE.get(n)
            return model.gen_disp[z, n, model.t.last(
            )] - model.gen_disp[z, n, t] <= model.ramp_dn_delta[z, n, t]
        # cemo.const.DEFAULT_GEN_RAMP_RATE.get(n)
        return model.gen_disp[z, n, model.t.prev(t)] - model.gen_disp[
            z, n, t] <= model.ramp_dn_delta[z, n, t]
    return Constraint.Skip


def con_uns(model, r):
    return sum(model.unserved[r, t] for t in model.t) \
        <= 0.00002 * sum(model.region_net_demand[r, t] for t in model.t)


def cost_capital(model):
    return sum(model.cost_gen_build[z, n] * (model.gen_cap_new[z, n] + model.gen_cap_exo[z, n])
               * model.fixed_charge_rate[n]
               for z in model.zones
               for n in model.gen_tech_per_zone[z])\
        + sum(model.cost_stor_build[z, s] * (model.stor_cap_new[z, s] + model.stor_cap_exo[z, s])
              * model.fixed_charge_rate[s]
              for z in model.zones
              for s in model.stor_tech_per_zone[z])\
        + sum(model.cost_hyb_build[z, h] * (model.hyb_cap_new[z, h] + model.hyb_cap_exo[z, h])
              * model.fixed_charge_rate[h]
              for z in model.zones
              for h in model.hyb_tech_per_zone[z])


def cost_fixed(model):
    return sum(model.cost_gen_fom[n] * model.gen_cap_op[z, n]
               for z in model.zones
               for n in model.gen_tech_per_zone[z])\
        + sum(model.cost_stor_fom[s] * model.stor_cap_op[z, s]
              for z in model.zones
              for s in model.stor_tech_per_zone[z])\
        + sum(model.cost_hyb_fom[h] * model.hyb_cap_op[z, h]
              for z in model.zones
              for h in model.hyb_tech_per_zone[z])


def cost_unserved(model):
    return model.year_correction_factor * model.cost_unserved * sum(
        model.unserved[r, t] for r in model.regions for t in model.t)


def cost_operating(model):
    return model.year_correction_factor * (
        sum(model.cost_gen_vom[n] * model.gen_disp[z, n, t]
            for z in model.zones for n in model.gen_tech_per_zone[z]
            for t in model.t) +
        sum(model.cost_fuel[z, f] * model.fuel_heat_rate[z, f] *
            model.gen_disp[z, f, t] for z in model.zones
            for f in model.fuel_gen_tech_per_zone[z] for t in model.t) + sum(
                model.cost_stor_vom[s] * model.stor_disp[z, s, t]
                for z in model.zones for s in model.stor_tech_per_zone[z]
                for t in model.t) + sum(
                    model.cost_hyb_vom[h] * model.hyb_disp[z, h, t]
                    for z in model.zones for h in model.hyb_tech_per_zone[z]
                    for t in model.t))


def cost_transmission(model):
    return model.year_correction_factor * model.cost_trans * sum(
        model.intercon_disp[r, p, t] for r in model.regions
        for p in model.intercon_per_region[r] for t in model.t)


def cost_emissions(model):
    return model.year_correction_factor * model.cost_emit * sum(
        emissions(model, r) for r in model.regions)


def cost_retirement(model):
    return sum(model.cost_retire[n] *
               (model.gen_cap_ret[z, n] + model.ret_gen_cap_exo[z, n])
               for z in model.zones for n in model.retire_gen_tech_per_zone[z])


def cost_shadow(model):
    return 10000000 * sum(model.gen_cap_ret_neg[z, n]
                          for z in model.zones
                          for n in model.retire_gen_tech_per_zone[z])\
        + 10000 * sum(model.surplus[r, t] for r in model.regions
                      for t in model.t)\
        + model.year_correction_factor * (
        sum(cemo.const.DEFAULT_GEN_RAMP_PENALTY.get(n, 0) * model.ramp_up_delta[z, n, t]
            for z in model.zones
            for n in model.gen_tech_per_zone[z]
            for t in model.t)
        + sum(cemo.const.DEFAULT_GEN_RAMP_PENALTY.get(n, 0) * model.ramp_dn_delta[z, n, t]
              for z in model.zones
              for n in model.gen_tech_per_zone[z]
              for t in model.t)
    )


def obj_cost(model):
    """Objective function as total annualised cost for model"""
    return cost_capital(model)\
        + cost_fixed(model) + cost_unserved(model) + cost_operating(model)\
        + cost_transmission(model) + cost_emissions(model)\
        + cost_retirement(model) + cost_shadow(model)
