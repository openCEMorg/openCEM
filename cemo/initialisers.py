"""Module to host initialisers for sets and parameters"""
__author__ = "José Zapata"
__copyright__ = "Copyright 2018, ITP Renewables, Australia"
__credits__ = ["José Zapata", "Dylan McConnell", "Navid Hagdadi"]
__license__ = "GPLv3"
__version__ = "0.9.2"
__maintainer__ = "José Zapata"
__email__ = "jose.zapata@itpau.com.au"
__status__ = "Development"
import calendar

import cemo.const


def init_year_correction_factor(model):
    '''Calculate factor to adjust dispatch periods different to 8760 hours'''
    ystr = model.t.last()
    year = int(ystr[:4])
    hours = 8760
    if calendar.isleap(year):
        hours = 8784
    return hours / len(model.t)


def init_zones_in_regions(model):
    '''Return zones in region tuples for declared regions'''
    for i in cemo.const.ZONES_IN_REGIONS:
        if i[0] in model.regions and i[1] in model.zones:
            yield i


def init_region_intercons(model):
    '''Return regional interconnectors for declared regions'''
    for i in cemo.const.REGION_INTERCONS:
        if i[0] in model.regions and i[1] in model.regions:
            yield i


def init_stor_rt_eff(model, tech):
    '''Default return efficiency for storage techs'''
    return cemo.const.DEFAULT_STOR_PROPS["rt_eff"].get(tech, 0)


def init_stor_charge_hours(model, tech):
    '''Default charge hours for storage tech'''
    return cemo.const.DEFAULT_STOR_PROPS["charge_hours"].get(tech, 0)


def init_hyb_col_mult(model, tech):
    '''Default collector multiple for hybrid tech'''
    return cemo.const.DEFAULT_HYB_PROPS["col_mult"].get(tech, 0)


def init_hyb_charge_hours(model, tech):
    '''Default charge hours for hybrid tech'''
    return cemo.const.DEFAULT_HYB_PROPS["charge_hours"].get(tech, 0)


def init_intercon_prop_factor(m, source, dest):
    '''Initialise interconnector proportioning factors'''
    return cemo.const.INTERCON_PROP_FACTOR.get(source).get(dest, 0)


def init_intercon_trans_limit(m, source, dest):
    return cemo.const.INTERCON_TRANS_LIMIT.get(source).get(dest)


def init_default_fuel_price(model, zone, tech):
    return cemo.const.DEFAULT_FUEL_PRICE.get(tech, 100.0)


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
    return cemo.const.GEN_CAP_FACTOR.get(tech, 0)


def init_max_hydro(model, zone):
    return cemo.const.DEFAULT_HYDRO_MWH_MAX.get(zone, 0)
