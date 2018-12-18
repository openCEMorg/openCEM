import pytest
from pyomo.environ import value


@pytest.mark.parametrize("zone,tech", [
    (16, 1),
    (16, 2),
    (16, 8),
    (16, 12),
])
def test_con_maxcap(solution, zone, tech):
    assert value(solution.gen_cap_op[zone, tech]) <= value(
        solution.gen_build_limit[zone, tech])


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
    assert pytest.approx(value(solution.gen_disp[zone, tech, time])
                         <= value(solution.gen_cap_factor[zone, tech, time])
                         * value(solution.gen_cap_op[zone, tech]))


@pytest.mark.parametrize("tech", [1, 2, 8, 12])
@pytest.mark.parametrize("zone", [16])
def test_con_opcap(solution, zone, tech):
    assert value(solution.gen_cap_op[zone, tech]) \
        == pytest.approx(value(solution.gen_cap_initial[zone, tech])\
        + value(solution.gen_cap_new[zone, tech]))

# TODO write the test for subsequent years
