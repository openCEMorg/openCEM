#!/bin/python3
# -*- coding: utf-8 -*-
# pylint: disable=bad-continuation
'''
openCEM module to convert simulation data into JSON outputs
'''
__author__ = "Andrew Hall"
__copyright__ = "Copyright 2018, ITP Renewables, Australia"
__credits__ = ["Andrew Hall", "José Zapata"]
__license__ = "GPLv3"
__version__ = "0.9.2"
__maintainer__ = "Andrew Hall"
__email__ = "andrew.hall@itpau.com.au"
__status__ = "Development"

from pyomo.environ import value

from cemo.rules import (cost_build_per_zone, cost_shadow,
                        cost_trans_build_per_zone)


def jsonify(inst):
    '''Produce full JSON model output'''
    out = {'sets':
           {
               inst.regions.name: list(inst.regions),
               inst.zones.name: list(inst.zones),
               inst.all_tech.name: list(inst.all_tech),
               inst.fuel_gen_tech.name: list(inst.fuel_gen_tech),
               inst.commit_gen_tech.name: list(inst.commit_gen_tech),
               inst.retire_gen_tech.name: list(inst.retire_gen_tech),
               inst.nobuild_gen_tech.name: list(inst.nobuild_gen_tech),
               inst.hyb_tech.name: list(inst.hyb_tech),
               inst.stor_tech.name: list(inst.stor_tech),
               inst.t.name: list(inst.t),
               inst.zones_in_regions.name: list(inst.zones_in_regions),
               inst.gen_tech_in_zones.name: list(inst.gen_tech_in_zones),
               inst.fuel_gen_tech_in_zones.name: list(inst.fuel_gen_tech_in_zones),
               inst.retire_gen_tech_in_zones.name: list(inst.retire_gen_tech_in_zones),
               inst.commit_gen_tech_in_zones.name: list(inst.commit_gen_tech_in_zones),
               inst.hyb_tech_in_zones.name: list(inst.hyb_tech_in_zones),
               inst.stor_tech_in_zones.name: list(inst.stor_tech_in_zones),
               inst.intercons_in_zones.name: list(inst.intercons_in_zones),
               # Complex sets of sets
               inst.zones_per_region.name: fill_complex_set(inst.zones_per_region),
               inst.gen_tech_per_zone.name: fill_complex_set(inst.gen_tech_per_zone),
               inst.fuel_gen_tech_per_zone.name: fill_complex_set(inst.fuel_gen_tech_per_zone),
               inst.retire_gen_tech_per_zone.name: fill_complex_set(inst.retire_gen_tech_per_zone),
               inst.commit_gen_tech_per_zone.name: fill_complex_set(inst.commit_gen_tech_per_zone),
               inst.hyb_tech_per_zone.name: fill_complex_set(inst.hyb_tech_per_zone),
               inst.stor_tech_per_zone.name: fill_complex_set(inst.stor_tech_per_zone),
               inst.intercon_per_zone.name: fill_complex_set(inst.intercon_per_zone)
           },
           'params': {
               # params with complex tuple keys
               inst.cost_gen_build.name: fill_complex_param(inst.cost_gen_build),
               inst.cost_stor_build.name: fill_complex_param(inst.cost_stor_build),
               inst.cost_hyb_build.name: fill_complex_param(inst.cost_hyb_build),
               inst.cost_intercon_build.name: fill_complex_param(inst.cost_intercon_build),
               inst.cost_fuel.name: fill_complex_param(inst.cost_fuel),
               inst.fuel_heat_rate.name: fill_complex_param(inst.fuel_heat_rate),
               inst.intercon_loss_factor.name: fill_complex_param(inst.intercon_loss_factor),
               inst.gen_cap_factor.name: fill_complex_param(inst.gen_cap_factor),
               inst.hyb_cap_factor.name: fill_complex_param(inst.hyb_cap_factor),
               inst.gen_build_limit.name: fill_complex_param(inst.gen_build_limit),
               inst.gen_cap_initial.name: fill_complex_param(inst.gen_cap_initial),
               inst.stor_cap_initial.name: fill_complex_param(inst.stor_cap_initial),
               inst.hyb_cap_initial.name: fill_complex_param(inst.hyb_cap_initial),
               inst.intercon_cap_initial.name: fill_complex_param(inst.intercon_cap_initial),
               inst.gen_cap_exo.name: fill_complex_param(inst.gen_cap_exo),
               inst.stor_cap_exo.name: fill_complex_param(inst.stor_cap_exo),
               inst.hyb_cap_exo.name: fill_complex_param(inst.hyb_cap_exo),
               inst.intercon_cap_exo.name: fill_complex_param(inst.intercon_cap_exo),
               inst.ret_gen_cap_exo.name: fill_complex_param(inst.ret_gen_cap_exo),
               inst.region_net_demand.name: fill_complex_param(inst.region_net_demand),

               # params with many scalar keys and
               inst.cost_gen_fom.name: fill_scalar_key_param(inst.cost_gen_fom),
               inst.cost_gen_vom.name: fill_scalar_key_param(inst.cost_gen_vom),
               inst.cost_stor_fom.name: fill_scalar_key_param(inst.cost_stor_fom),
               inst.cost_stor_vom.name: fill_scalar_key_param(inst.cost_stor_vom),
               inst.cost_hyb_fom.name: fill_scalar_key_param(inst.cost_hyb_fom),
               inst.cost_hyb_vom.name: fill_scalar_key_param(inst.cost_hyb_vom),
               inst.all_tech_lifetime.name: fill_scalar_key_param(inst.all_tech_lifetime),
               inst.fixed_charge_rate.name: fill_scalar_key_param(inst.fixed_charge_rate),
               inst.cost_retire.name: fill_scalar_key_param(inst.cost_retire),
               inst.stor_rt_eff.name: fill_scalar_key_param(inst.stor_rt_eff),
               inst.stor_charge_hours.name: fill_scalar_key_param(inst.stor_charge_hours),
               inst.hyb_col_mult.name: fill_scalar_key_param(inst.hyb_col_mult),
               inst.hyb_charge_hours.name: fill_scalar_key_param(inst.hyb_charge_hours),
               inst.fuel_emit_rate.name: fill_scalar_key_param(inst.fuel_emit_rate),
               inst.cost_cap_carry_forward.name: fill_scalar_key_param(inst.cost_cap_carry_forward),

               # params with scalar value
               inst.cost_unserved.name: inst.cost_unserved.value,
               inst.cost_emit.name: inst.cost_emit.value,
               inst.cost_trans.name: inst.cost_trans.value,
               inst.all_tech_discount_rate.name: inst.all_tech_discount_rate.value,
               inst.year_correction_factor.name: inst.year_correction_factor.value,
               inst.intercon_fixed_charge_rate.name: inst.intercon_fixed_charge_rate.value,


           },
           'vars': {
               inst.gen_cap_new.name: fill_complex_var(inst.gen_cap_new),
               inst.gen_cap_op.name: fill_complex_var(inst.gen_cap_op),
               inst.stor_cap_new.name: fill_complex_var(inst.stor_cap_new),
               inst.stor_cap_op.name: fill_complex_var(inst.stor_cap_op),
               inst.hyb_cap_new.name: fill_complex_var(inst.hyb_cap_new),
               inst.hyb_cap_op.name: fill_complex_var(inst.hyb_cap_op),
               inst.intercon_cap_new.name: fill_complex_var(inst.intercon_cap_new),
               inst.intercon_cap_op.name: fill_complex_var(inst.intercon_cap_op),
               inst.gen_cap_ret.name: fill_complex_var(inst.gen_cap_ret),
               inst.gen_cap_ret_neg.name: fill_complex_var(inst.gen_cap_ret_neg),
               inst.gen_cap_exo_neg.name: fill_complex_var(inst.gen_cap_exo_neg),
               inst.gen_disp.name: fill_complex_var(inst.gen_disp),
               inst.stor_disp.name: fill_complex_var(inst.stor_disp),
               inst.stor_charge.name: fill_complex_var(inst.stor_charge),
               inst.hyb_disp.name: fill_complex_var(inst.hyb_disp),
               inst.hyb_charge.name: fill_complex_var(inst.hyb_charge),
               inst.stor_level.name: fill_complex_var(inst.stor_level),
               inst.hyb_level.name: fill_complex_var(inst.hyb_level),
               inst.unserved.name: fill_complex_var(inst.unserved),
               inst.surplus.name: fill_complex_var(inst.surplus),
               inst.intercon_disp.name: fill_complex_var(inst.intercon_disp)
           },
           'duals': {
               'srmc': fill_dual_suffix(inst.dual, inst.ldbal)
           },
           'objective_value': value(inst.Obj - cost_shadow(inst))
           }
    if hasattr(inst, 'nem_year_emit_limit'):
        out['params'].update(
            {inst.nem_year_emit_limit.name: inst.nem_year_emit_limit.value})
    if hasattr(inst, 'nem_ret_ratio'):
        out['params'].update(
            {inst.nem_ret_ratio.name: inst.nem_ret_ratio.value})
    if hasattr(inst, 'nem_ret_gwh'):
        out['params'].update({inst.nem_ret_gwh.name: inst.nem_ret_gwh.value})
    if hasattr(inst, 'region_ret_ratio'):
        out['params'].update(
            {inst.region_ret_ratio.name: fill_scalar_key_param(inst.region_ret_ratio)})
    if hasattr(inst, 'nem_disp_ratio'):
        out['params'].update(
            {inst.nem_disp_ratio.name: inst.nem_disp_ratio.value})
    if hasattr(inst, 'nem_re_disp_ratio'):
        out['params'].update(
            {inst.nem_re_disp_ratio.name: inst.nem_re_disp_ratio.value})
    return out


def jsoninit(inst):
    '''Produce JSON output sufficient to initialise a cemo model'''
    inp = jsonify(inst)
    out = {}
    out.update(inp['sets'])
    out.update(inp['params'])

    del out['zones_per_region']
    del out['gen_tech_per_zone']
    del out['fuel_gen_tech_per_zone']
    del out['retire_gen_tech_per_zone']
    del out['hyb_tech_per_zone']
    del out['stor_tech_per_zone']
    del out['intercon_per_region']
    for entry in out:
        if isinstance(out[entry], dict):
            out.update({entry: simple_as_complex(out[entry])})

    return out


def json_carry_forward_cap(inst):
    '''Produce JSON output of capacity data to carry forward to next investment period'''
    out = {
        inst.gen_cap_initial.name: fill_complex_var(inst.gen_cap_op),
        inst.stor_cap_initial.name: fill_complex_var(inst.stor_cap_op),
        inst.hyb_cap_initial.name: fill_complex_var(inst.hyb_cap_op),
        inst.intercon_cap_initial.name: fill_complex_var(inst.intercon_cap_op),
        inst.cost_cap_carry_forward.name: [
            {
                "index": zone, "value": value(cost_build_per_zone(inst, zone) + cost_trans_build_per_zone(inst, zone))
            }
            for zone in inst.zones]
    }
    return out


def jsonopcap0(inst):
    '''Produce JSON of starting capacity for current period from instance'''
    out = {inst.gen_cap_initial.name: fill_complex_param(inst.gen_cap_initial),
           inst.stor_cap_initial.name: fill_complex_param(inst.stor_cap_initial),
           inst.hyb_cap_initial.name: fill_complex_param(inst.hyb_cap_initial)}
    return out


def jsonifyld(inst):
    '''Produce JSON net demand indexed by region and timestamp'''
    out = fill_complex_param(inst.region_net_demand)
    return out


# Helper functions for marshalling various objects into appropriate json values

def fill_complex_set(pset):
    '''Return indexed set dictionary'''
    out = dict()
    for i in pset.keys():
        out[str(i)] = list(pset[i])

    return out


def fill_complex_param(par):
    ''''Return indexed parameter dictionary'''
    out = []
    for i in par.keys():
        out.append({'index': i, 'value': par[i]})
    return out


def fill_complex_mutable_param(par):
    '''Return complex mutable parameter dictionary'''
    out = []
    for i in par.keys():
        out.append({'index': i, 'value': par[i].value})
    return out


def fill_scalar_key_param(par):
    '''Return scalar key parameter dictionary'''
    out = dict()
    for i in par.keys():
        out[str(i)] = par[i]

    return out


def fill_complex_var(var):
    '''Return complex variable dictionary'''
    out = []
    for i in var.keys():
        out.append({'index': i, 'value': 0 if 1e-6 < var[i].value < 0 else var[i].value})

    return out


def fill_dual_suffix(dual, name):
    '''Return dual suffix dictionary'''
    out = []
    for i in name:
        out.append({'index': i, 'value': dual[name[i]]})

    return out


def simple_as_complex(dic):
    '''Return a complex index dictionary from a simple dictionary'''
    out = []
    for i in dic:
        out.append({'index': int(i), 'value': dic[i]})
    return out
