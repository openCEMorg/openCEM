"""Module to host all the rules applied to model"""
__author__ = "José Zapata"
__copyright__ = "Copyright 2018, ITP Renewables, Australia"
__credits__ = ["José Zapata", "Dylan McConnell", "Navid Hagdadi"]
__license__ = "GPLv3"
__version__ = "0.9.2"
__maintainer__ = "José Zapata"
__email__ = "jose.zapata@itpau.com.au"
__status__ = "Development"
from pyomo.environ import Constraint

import cemo.const


def ScanForTechperZone(model):
    '''generate sparse generator zone sets from tuple based sets'''
    for (i, j) in model.gen_tech_in_zones:
        model.gen_tech_per_zone[i].add(j)
    for (i, j) in model.retire_gen_tech_in_zones:
        model.retire_gen_tech_per_zone[i].add(j)
    for (i, j) in model.fuel_gen_tech_in_zones:
        model.fuel_gen_tech_per_zone[i].add(j)
    for (i, j) in model.commit_gen_tech_in_zones:
        model.commit_gen_tech_per_zone[i].add(j)
    for (i, j) in model.re_gen_tech_in_zones:
        model.re_gen_tech_per_zone[i].add(j)
    for (i, j) in model.disp_gen_tech_in_zones:
        model.disp_gen_tech_per_zone[i].add(j)
    for (i, j) in model.re_disp_gen_tech_in_zones:
        model.re_disp_gen_tech_per_zone[i].add(j)


def ScanForStorageperZone(model):
    '''generate sparse storage zone sets from tuple based sets'''
    for (i, j) in model.stor_tech_in_zones:
        model.stor_tech_per_zone[i].add(j)


def ScanForHybridperZone(model):
    '''generate hybrid generator zone sets from tuple based sets'''
    for (i, j) in model.hyb_tech_in_zones:
        model.hyb_tech_per_zone[i].add(j)


def ScanForZoneperRegion(model):
    '''Generate tuples of zones in regions based on default or configured data'''
    for (i, j) in model.zones_in_regions:
        if i in model.regions:
            model.zones_per_region[i].add(j)


def ScanForTransLineperRegion(model):
    '''Generate (source,target) interconnector tuples based on default or configured data'''
    for (i, j) in model.region_intercons:
        model.intercon_per_region[i].add(j)


def dispatch(model, r):
    '''calculate sum of all dispatch'''
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


def emissions(model, r):
    '''calculate emissions in kg'''
    return (sum(model.fuel_emit_rate[n] * model.gen_disp[z, n, t]
                for z in model.zones_per_region[r]
                for n in model.fuel_gen_tech_per_zone[z]
                for t in model.t) +
            sum(model.fuel_emit_rate[n] * model.gen_disp_com_p[z, n, t]
                for z in model.zones_per_region[r]
                for n in model.commit_gen_tech_per_zone[z]
                for t in model.t))


def con_nem_ret_ratio(model):
    '''inequality constraint defining renewable generation must be greater
       or equal than total generation times ret ratio'''
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


# TODO a more transparent method to scale gwh from config file to mwh in model


def con_nem_ret_gwh(model):
    '''inequality constraint setting renewable generation must be greater or equal
    than a defined GWh per year across the system'''
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
        >= model.nem_ret_gwh * 1000 / model.year_correction_factor


def con_nem_disp_ratio(model, r, t):
    '''inequality constraint setting dispatchable generation must be greater than
    disp_ratio * total generation, in each region and each hour'''
    return sum(model.gen_disp[z, n, t]
               for z in model.zones_per_region[r]
               for n in model.disp_gen_tech_per_zone[z]
               )\
        + sum(model.stor_disp[z, s, t]
              for z in model.zones_per_region[r]
              for s in model.stor_tech_per_zone[z]
              )\
        + sum(model.hyb_disp[z, h, t]
              for z in model.zones_per_region[r]
              for h in model.hyb_tech_per_zone[z]
              )\
        >= model.nem_disp_ratio * (sum(model.gen_disp[z, n, t]
                                       for z in model.zones_per_region[r]
                                       for n in model.gen_tech_per_zone[z]
                                       )
                                   + sum(model.stor_disp[z, s, t]
                                         for z in model.zones_per_region[r]
                                         for s in model.stor_tech_per_zone[z]
                                         )
                                   + sum(model.hyb_disp[z, h, t]
                                         for z in model.zones_per_region[r]
                                         for h in model.hyb_tech_per_zone[z]
                                         )
                                   )


def con_nem_re_disp_ratio(model, r, t):
    '''inequality constraint setting renewable dispatchable generation must be greater than
    disp_ratio * total generation, in each region and each hour'''
    return sum(model.gen_disp[z, n, t]
               for z in model.zones_per_region[r]
               for n in model.re_disp_gen_tech_per_zone[z]
               )\
        + sum(model.stor_disp[z, s, t]
              for z in model.zones_per_region[r]
              for s in model.stor_tech_per_zone[z]
              )\
        + sum(model.hyb_disp[z, h, t]
              for z in model.zones_per_region[r]
              for h in model.hyb_tech_per_zone[z]
              )\
        >= model.nem_re_disp_ratio * (sum(model.gen_disp[z, n, t]
                                          for z in model.zones_per_region[r]
                                          for n in model.gen_tech_per_zone[z]
                                          )
                                      + sum(model.stor_disp[z, s, t]
                                            for z in model.zones_per_region[r]
                                            for s in model.stor_tech_per_zone[z]
                                            )
                                      + sum(model.hyb_disp[z, h, t]
                                            for z in model.zones_per_region[r]
                                            for h in model.hyb_tech_per_zone[z]
                                            )
                                      )


def con_region_ret_ratio(model, r):
    '''inequality constraint setting renewable generation must be greater than
    ratio * total generation, in each region'''
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


def con_max_mwh_as_cap_factor(model, zone, tech):
    '''Define a maximum MWh output as a capacity factor cap for a zone and technology'''
    cap_factor = cemo.const.MAX_MWH_CAP_FACTOR.get(zone).get(tech, 1)
    if cap_factor < 1:
        return sum(model.gen_disp[zone, tech, t]
                   for t in model.t)\
            <= cap_factor * model.gen_cap_op[zone, tech] * 8760 /\
            model.year_correction_factor
    return Constraint.Skip


def con_maxmhw(model, z, n):
    '''limit maximum generation over a period, scaled to yearly'''
    if n == 18:  # hydro only
        return sum(model.gen_disp[z, n, t] for t in model.t)\
            <= model.hydro_gen_mwh_limit[z] / model.year_correction_factor
    return Constraint.Skip


def con_maxtrans(model, r, p, t):
    '''limit transmission per link to be less than its maximum'''
    return model.intercon_disp[r, p, t] <= model.intercon_trans_limit[r, p]


def con_chargelim(model, z, s, t):
    '''limit flow of charge to storage to be less than storage nameplate capacity'''
    return model.stor_charge[z, s, t] <= model.stor_cap_op[z, s]


def con_dischargelim(model, z, s, t):
    '''limit flow of energy out of storage to be less than its nameplate capacity'''
    return model.stor_disp[z, s, t] <= model.stor_cap_op[z, s]


def con_maxcharge(model, z, s, t):
    '''Storage charge must not exceed maximum capacity'''
    return model.stor_level[z, s, t] \
        <= model.stor_cap_op[z, s] * model.stor_charge_hours[s]


def con_storcharge(model, z, s, t):
    '''Storage charge dynamic'''
    return model.stor_level[z, s, t] \
        == model.stor_level[z, s, model.t.prevw(t)] \
        - model.stor_disp[z, s, t] + \
        model.stor_rt_eff[s] * model.stor_charge[z, s, t]


def con_hybcharge(model, z, h, t):
    '''Hybrid charge dynamic'''
    return model.hyb_level[z, h, t] \
        == model.hyb_level[z, h, model.t.prevw(t)] \
        - model.hyb_disp[z, h, t] \
        + model.hyb_charge[z, h, t]


def con_chargelimhy(model, z, h, t):
    '''Hybrid storage cannot charge faster than what the collector can charge it'''
    return model.hyb_charge[z, h, t] \
        <= model.hyb_col_mult[h] * model.hyb_cap_factor[z, h, t] * model.hyb_cap_op[z, h]


def con_dischargelimhy(model, z, h, t):
    '''Hybrid storage cannot discharge faster than plant nameplate capacity'''
    return model.hyb_disp[z, h, t] <= model.hyb_cap_op[z, h]


def con_maxchargehy(model, z, h, t):
    '''Hybrid storage cannot charge beyond its maximum charge capacity'''
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
        + sum((1.0 + model.intercon_prop_factor[r, p]) * model.intercon_disp[r, p, t]
              for p in model.intercon_per_region[r])\
        + sum(model.stor_charge[z, s, t]
              for z in model.zones_per_region[r] for s in model.stor_tech_per_zone[z])\
        + model.surplus[r, t]


def con_maxcap(model, z, n):
    '''Prevent resulting operational capacity to exceed build limits'''
    return model.gen_cap_op[z, n] <= model.gen_build_limit[z, n]


def con_emissions(model):
    '''Emission constraint for the NEM in MT/y for total emissions'''
    return model.year_correction_factor * sum(
        emissions(model, r)
        for r in model.regions) <= 1e9 * model.nem_year_emit_limit


def con_slackretire(model, z, n):
    '''Adjust for exogenous retires exceeding existing capacity'''
    return model.gen_cap_initial[z, n] - model.ret_gen_cap_exo[
        z, n] + model.gen_cap_ret_neg[z, n] >= 0


def con_slackbuild(model, z, n):
    '''Adjust for exogenous builds exceding build limits'''
    return model.gen_cap_initial[z, n] + model.gen_cap_exo[
        z, n] - model.gen_cap_exo_neg[z, n] <= model.gen_build_limit[z, n]


def con_opcap(model, z, n):  # z and n come both from TechinZones
    '''Calculate operating capacity as the net of model and exogenous decisions'''
    if n in model.nobuild_gen_tech:
        if n in model.retire_gen_tech:
            return model.gen_cap_op[z, n] == model.gen_cap_initial[z, n] \
                + (model.gen_cap_exo[z, n] - model.gen_cap_exo_neg[z, n])\
                - model.gen_cap_ret[z, n] - \
                (model.ret_gen_cap_exo[z, n] - model.gen_cap_ret_neg[z, n])
        return model.gen_cap_op[z, n] == model.gen_cap_initial[z, n] \
            + (model.gen_cap_exo[z, n] - model.gen_cap_exo_neg[z, n])

    if n in model.retire_gen_tech:
        return model.gen_cap_op[z, n] == model.gen_cap_initial[z, n] \
            + (model.gen_cap_exo[z, n] - model.gen_cap_exo_neg[z, n])\
            + model.gen_cap_new[z, n]\
            - model.gen_cap_ret[z, n] - \
            (model.ret_gen_cap_exo[z, n] - model.gen_cap_ret_neg[z, n])
    return model.gen_cap_op[z, n] == model.gen_cap_initial[z, n]\
        + (model.gen_cap_exo[z, n] - model.gen_cap_exo_neg[z, n])\
        + model.gen_cap_new[z, n]


def con_stcap(model, z, s):  # z and n come both from TechinZones
    '''Calculate Storage capacity as the net of model and exogenous decisions'''
    if s in model.nobuild_gen_tech:
        return model.stor_cap_op[z, s] == model.stor_cap_initial[z, s] \
            + model.stor_cap_exo[z, s]
    return model.stor_cap_op[z, s] == model.stor_cap_initial[z, s]\
        + model.stor_cap_exo[z, s]\
        + model.stor_cap_new[z, s]


def con_hycap(model, z, h):  # z and n come both from TechinZones
    '''Calculate Hybrid capacity as the net of model and exogenous decisions'''
    if h in model.nobuild_gen_tech:
        return model.hyb_cap_op[z, h] == model.hyb_cap_initial[z, h] \
            + model.hyb_cap_exo[z, h]
    return model.hyb_cap_op[z, h] == model.hyb_cap_initial[z, h]\
        + model.hyb_cap_exo[z, h]\
        + model.hyb_cap_new[z, h]


def con_caplim(model, z, n, t):  # z and n come both from TechinZones
    '''Dispatch within the hourly limit on capacity factor for operating capacity'''
    if cemo.const.GEN_COMMIT['penalty'].get(n) is not None:
        return model.gen_disp_com[
            z, n, t] <= model.gen_cap_factor[z, n, t] * model.gen_cap_op[z, n]
    return model.gen_disp[z, n, t] \
        <= model.gen_cap_factor[z, n, t] * model.gen_cap_op[z, n]


def con_min_load_commit(model, z, n, t):
    '''Dispatch at least min % pct of committed capacity'''
    mincap = cemo.const.GEN_COMMIT['mincap'].get(n)
    return model.gen_disp[z, n, t] >= mincap * model.gen_disp_com[z, n, t]


def con_disp_ramp_down(model, z, n, t):
    '''dispatch less than ramp down commitment'''
    ramp_dn = cemo.const.GEN_COMMIT['rate down'].get(n)
    return model.gen_disp[z, n, t] <= model.gen_disp_com[z, n, t] +\
        (ramp_dn - 1) * model.gen_disp_com_m[z, n, model.t.nextw(t)]


def con_disp_ramp_up(model, z, n, t):
    '''dispatch less than ramp up commitment'''
    ramp_up = cemo.const.GEN_COMMIT['rate up'].get(n)
    return model.gen_disp[z, n, t] <= model.gen_disp_com[z, n, model.t.prevw(t)] + \
        ramp_up * model.gen_disp_com_p[z, n, t]


def con_ramp_down_uptime(model, z, n, t):
    '''commitment ramp down must respect up - time minimum'''
    return model.gen_disp_com_m[z, n, t] <= model.gen_disp_com_s[z, n, t]


def con_uptime_commitment(model, z, n, t):
    '''capacity that can be switched off, observing up - time'''
    uptime = cemo.const.GEN_COMMIT['uptime'].get(n)
    return model.gen_disp_com_s[z, n, t] == model.gen_disp_com_s[z, n, model.t.prevw(t)] +\
        model.gen_disp_com_p[z, n, model.t.prevw(
            t, k=uptime)] - model.gen_disp_com_m[z, n, t]


def con_committed_cap(model, z, n, t):
    '''Committed capacity for each time step'''
    return model.gen_disp_com[z, n, t] == model.gen_disp_com[z, n, model.t.prevw(t)] -\
        model.gen_disp_com_m[z, n, t] + \
        model.gen_disp_com_p[z, n, model.t.prevw(t)]


def con_uns(model, r):
    '''constraint limiting unserved energy'''
    return sum(model.unserved[r, t] for t in model.t) \
        <= 0.00002 * sum(model.region_net_demand[r, t] for t in model.t)


def cost_capital(model, z):
    '''calculate build costs'''
    return sum(model.cost_gen_build[z, n] * (model.gen_cap_new[z, n] + model.gen_cap_exo[z, n])
               * model.fixed_charge_rate[n]
               for n in model.gen_tech_per_zone[z])\
        + sum(model.cost_stor_build[z, s] * (model.stor_cap_new[z, s] + model.stor_cap_exo[z, s])
              * model.fixed_charge_rate[s]
              for s in model.stor_tech_per_zone[z])\
        + sum(model.cost_hyb_build[z, h] * (model.hyb_cap_new[z, h] + model.hyb_cap_exo[z, h])
              * model.fixed_charge_rate[h]
              for h in model.hyb_tech_per_zone[z])\
        + model.cost_cap_carry_forward[z]


def cost_fixed(model):
    ''' calculate FOM costs'''
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
    '''Calculate yearly adjusted USE costs'''
    return model.year_correction_factor * model.cost_unserved * sum(
        model.unserved[r, t] for r in model.regions for t in model.t)


def cost_operating(model):
    '''Calculate operating costs as the sum of FOM, VOM
    and fuel costs for generators, hybrid and storage'''
    return model.year_correction_factor * (
        sum(model.cost_gen_vom[n] * model.gen_disp[z, n, t]
            for z in model.zones for n in model.gen_tech_per_zone[z]
            for t in model.t) +
        sum(model.cost_fuel[z, f] * model.fuel_heat_rate[z, f] *
            model.gen_disp[z, f, t] for z in model.zones
            for f in model.fuel_gen_tech_per_zone[z]
            for t in model.t) +
        sum(model.cost_stor_vom[s] * model.stor_disp[z, s, t]
            for z in model.zones for s in model.stor_tech_per_zone[z]
            for t in model.t) +
        sum(model.cost_hyb_vom[h] * model.hyb_disp[z, h, t]
            for z in model.zones
            for h in model.hyb_tech_per_zone[z] for t in model.t) +
        sum(model.cost_fuel[z, n] *
            cemo.const.GEN_COMMIT['penalty'].get(
                n, 0) * model.gen_disp_com_p[z, n, t]
            for z in model.zones
            for n in model.commit_gen_tech_per_zone[z]
            for t in model.t))


def cost_transmission(model):
    '''Calculate transmission flow costs'''
    return model.year_correction_factor * model.cost_trans * sum(
        model.intercon_disp[r, p, t] for r in model.regions
        for p in model.intercon_per_region[r] for t in model.t)


def cost_emissions(model):
    '''Calculate emission costs from all fuel based generators
    times their respective emissions rate'''
    return model.year_correction_factor * model.cost_emit * sum(
        emissions(model, r) for r in model.regions)


def cost_retirement(model):
    '''Calculate retirment costs for all retired capacity'''
    return sum(model.cost_retire[n] *
               (model.gen_cap_ret[z, n] + model.ret_gen_cap_exo[z, n])
               for z in model.zones for n in model.retire_gen_tech_per_zone[z])


def cost_shadow(model):
    '''Calculate shadow costs, i.e. penalties applied to
    ensure numerical stability of model'''
    return 10000000 * sum(model.gen_cap_ret_neg[z, n]
                          for z in model.zones
                          for n in model.retire_gen_tech_per_zone[z])\
        + 10000000 * sum(model.gen_cap_exo_neg[z, n]
                         for z in model.zones
                         for n in model.gen_tech_per_zone[z])\
        + 10000 * sum(model.surplus[r, t] for r in model.regions
                      for t in model.t)


def obj_cost(model):
    """Objective function as total annualised cost for model"""
    return sum(cost_capital(model, z) for z in model.zones)\
        + cost_fixed(model) + cost_unserved(model) + cost_operating(model)\
        + cost_transmission(model) + cost_emissions(model)\
        + cost_retirement(model) + cost_shadow(model)
