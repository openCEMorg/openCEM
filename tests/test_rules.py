'''Test suite to check model rules'''

import pytest
from pyomo.environ import value

from cemo.rules import con_caplim, con_maxcap, con_opcap, dispatch


@pytest.mark.parametrize("zone,tech", [
    (16, 1),
    (16, 2),
    (16, 8),
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
    assert pytest.approx(value(con_opcap(solution, zone, tech)))


@pytest.mark.parametrize("region", [4, 5])
def test_dispatch(solution, region):
    '''Assert solution dispatch matches benchmark'''
    assert pytest.approx(value(dispatch(solution, region)))
