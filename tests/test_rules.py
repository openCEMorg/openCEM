'''Test suite to check model rules and initialisers'''

import pytest
from pyomo.environ import value

from cemo.initialisers import init_zone_demand_factors
from cemo.rules import con_caplim, con_maxcap, con_gen_cap, dispatch
from cemo.const import ZONE_DEMAND_PCT


@pytest.mark.parametrize("zone,tech", [
    (11, 11),
    (16, 12),
])
def test_con_maxcap(solution, zone, tech):
    '''Assert solution obeys maximum capacity constraints'''
    assert pytest.approx(value(con_maxcap(solution, zone, tech)))


@pytest.mark.parametrize("zone,tech", [
    (16, 1),
    (16, 2),
    (16, 8),
    (16, 12),
])
@pytest.mark.parametrize("time", [
    '2020-01-01 11:00:00',
    '2020-01-01 21:00:00',
])
def test_con_caplim(solution, zone, tech, time):
    '''Assert solution obeys capacity factor limitation constraint'''
    assert pytest.approx(value(con_caplim(solution, zone, tech, time)))


@pytest.mark.parametrize("zone,tech", [
    (9, 6),
    (16, 1),
    (16, 2),
    (16, 8),
    (16, 12)
])
def test_con_opcap(solution, zone, tech):
    '''Assert solution computes same operating capacity as benchmark'''
    assert pytest.approx(value(con_gen_cap(solution, zone, tech)))


@pytest.mark.parametrize("region", [4, 5])
def test_dispatch(solution, region):
    '''Assert solution dispatch matches benchmark'''
    assert pytest.approx(value(dispatch(solution, region)))


@pytest.mark.parametrize("zone,time,result", [
    (6, '2019-04-30 11:00:00', ZONE_DEMAND_PCT.get(6).get('peak')),  # peak time (weekdays 8 and 20 hrs)
    (2, '2019-05-01 05:00:00', ZONE_DEMAND_PCT.get(2).get('off peak')),  # off peak time afterhours
    (13, '2019-04-27 14:00:00', ZONE_DEMAND_PCT.get(13).get('off peak')),  # off peak weekend
    (4, '2025-01-01 11:00:00', ZONE_DEMAND_PCT.get(4).get('off peak')),  # off peak holiday AUS wide
    (3, '2019-05-06 11:00:00', ZONE_DEMAND_PCT.get(3).get('off peak')),  # off peak Labour day QLD
    (8, '2019-05-06 11:00:00', ZONE_DEMAND_PCT.get(8).get('peak')),  # peak (not) Labour day NSW
])
def test_zone_factor(zone, time, result):
    '''Assert initialiser returns correct factor for zone demand proportioning'''
    assert result == pytest.approx(init_zone_demand_factors(None, zone, time))
