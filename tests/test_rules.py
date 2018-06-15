import pytest
from pyomo.environ import value


@pytest.mark.parametrize("region,time", [
    (4, '2020-01-01 01:00:00'),
    (4, '2020-01-01 21:00:00'),
])
def test_ldbal(solution, region, time):
    assert pytest.approx(sum(value(solution.q[z, n, time]) for z in solution.Z
                             for n in solution.TechperZone[z])
                         + value(solution.quns[region, time])
                         == value(solution.Ld[region, time])
                         + sum(value(solution.surplus[z, n, time])
                               for z in solution.Z
                               for n in solution.TechperZone[z]))


@pytest.mark.parametrize("zone,tech", [
    (16, 1),
    (16, 2),
    (16, 8),
    (16, 12),
])
def test_con_maxcap(solution, zone, tech):
    assert value(solution.OpCap[zone, tech, 2020]) <= value(
        solution.MaxCap[zone, tech])


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
    assert pytest.approx(value(solution.q[zone, tech, time])
                         + value(solution.surplus[zone, tech, time])
                         <= value(solution.capf[zone, tech, time])
                         * value(solution.OpCap[zone, tech, 2020]))


@pytest.mark.parametrize("tech", [1, 2, 8, 12])
@pytest.mark.parametrize("zone,Inv", [(16, 2020)])
def test_con_opcap(solution, zone, tech, Inv):
    assert value(solution.OpCap[zone, tech, Inv]) \
        == value(solution.OpCap0[zone, tech])\
        + value(solution.NewCap[zone, tech, Inv])

# TODO write the test for subsequent years
