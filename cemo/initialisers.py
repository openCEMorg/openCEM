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
import datetime

import cemo.const
import holidays


def init_year_correction_factor(model):
    # pylint: disable=unused-argument
    '''Calculate factor to adjust dispatch periods different to 8760 hours'''
    ystr = model.t.last()
    year = int(ystr[:4])
    hours = 8760
    if calendar.isleap(year):
        hours = 8784
    return hours / len(model.t)


def init_zones_in_regions(model):
    # pylint: disable=unused-argument
    '''Return zones in region tuples for declared regions'''
    for i in cemo.const.ZONES_IN_REGIONS:
        if i[0] in model.regions and i[1] in model.zones:
            yield i


def init_zone_intercons(model):
    # pylint: disable=unused-argument
    '''Return zone interconnector pairs for declared zones'''
    for zone_pair in [(zone_source, zone_dest)
                      for zone_source in cemo.const.ZONE_INTERCONS
                      for zone_dest in cemo.const.ZONE_INTERCONS[zone_source]]:
        if zone_pair[0] in model.zones and zone_pair[1] in model.zones:
            yield zone_pair


def init_stor_rt_eff(model, tech):
    # pylint: disable=unused-argument
    '''Default return efficiency for storage techs'''
    return cemo.const.DEFAULT_STOR_PROPS["rt_eff"].get(tech, 0)


def init_stor_charge_hours(model, tech):
    # pylint: disable=unused-argument
    '''Default charge hours for storage tech'''
    return cemo.const.DEFAULT_STOR_PROPS["charge_hours"].get(tech, 0)


def init_zone_demand_factors(model, zone, timestamp):
    dt = datetime.datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
    is_holiday = dt.date() not in holidays.AU(prov=cemo.const.ZONE_DEMAND_PCT.get(zone).get('prov'))
    print(is_holiday)
    is_peak = 'off peak'
    if dt.weekday() < 5 and 8 <= dt.hour < 20 and is_holiday:
        is_peak = 'peak'
    return cemo.const.ZONE_DEMAND_PCT.get(zone).get(is_peak)


def init_hyb_col_mult(model, tech):
    # pylint: disable=unused-argument
    '''Default collector multiple for hybrid tech'''
    return cemo.const.DEFAULT_HYB_PROPS["col_mult"].get(tech, 0)


def init_hyb_charge_hours(model, tech):
    # pylint: disable=unused-argument
    '''Default charge hours for hybrid tech'''
    return cemo.const.DEFAULT_HYB_PROPS["charge_hours"].get(tech, 0)


def init_intercon_prop_factor(model, source, dest):
    # pylint: disable=unused-argument
    '''Initialise interconnector proportioning factors'''
    return cemo.const.ZONE_INTERCONS.get(source).get(dest).get('loss', 0)


def init_intercon_trans_limit(model, source, dest):
    # pylint: disable=unused-argument
    '''Initialise interconector transmission limits'''
    return cemo.const.ZONE_INTERCONS.get(source).get(dest).get('limit')


def init_default_fuel_price(model, zone, tech):
    # pylint: disable=unused-argument
    '''Assign default price across zone and technologies'''
    return cemo.const.DEFAULT_FUEL_PRICE.get(tech, 100.0)


def init_default_heat_rate(model, zone, tech):
    # pylint: disable=unused-argument
    '''Initialise default heat rate for fuel based generators in each zone'''
    return cemo.const.DEFAULT_HEAT_RATE.get(tech, 15.0)


def init_default_fuel_emit_rate(model, tech):
    # pylint: disable=unused-argument
    '''Default fuel emission rate for fuel based generators'''
    return cemo.const.DEFAULT_FUEL_EMIT_RATE.get(tech, 800)


def init_cost_retire(model, tech):
    # pylint: disable=unused-argument
    '''Default retirement/rehabilitation cost in $/MW per technology'''
    return cemo.const.DEFAULT_RETIREMENT_COST.get(tech, 60000.0)


def init_default_lifetime(model, tech):
    # pylint: disable=unused-argument
    '''Default lifetime for technologies'''
    return cemo.const.DEFAULT_TECH_LIFETIME.get(tech, 30.0)


def init_gen_build_limit(model, zone, tech):
    # pylint: disable=unused-argument
    ''' Default build limits per technology and per zone'''
    return cemo.const.DEFAULT_BUILD_LIMIT.get(zone).get(tech, 100000)


def init_fcr(model, tech):
    # pylint: disable=unused-argument
    '''Calculate fixed charge rate for each technology'''
    return model.all_tech_discount_rate / (
        (model.all_tech_discount_rate + 1)**model.all_tech_lifetime[tech] -
        1) + model.all_tech_discount_rate


def init_cap_factor(model, zone, tech, time):
    # pylint: disable=unused-argument
    '''Default capacity factor per hour per technology and per zone.
        Note:Default to zero means technology does not generate'''
    return cemo.const.GEN_CAP_FACTOR.get(tech, 0)


def init_max_hydro(model, zone):
    # pylint: disable=unused-argument
    '''Default maximum hydro generation per year in each zone'''
    return cemo.const.DEFAULT_HYDRO_MWH_MAX.get(zone, 0)
