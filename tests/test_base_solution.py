'''Test suite for basic checking of model solution'''

import pytest

from pyomo.environ import value


@pytest.mark.parametrize("zone,tech", [
    (16, 1),
    (16, 2),
    (16, 8),
    (16, 12),
])
def test_capacities(solution, benchmark, zone, tech):
    '''Assert solution capacity decisions match known value'''
    assert value(solution.gen_cap_new[zone, tech]) \
        == pytest.approx(value(benchmark.gen_cap_new[zone, tech]))


@pytest.mark.parametrize("zone,time", [
    (16, '2020-01-02 10:00:00'),
    (16, '2020-01-02 14:00:00'),
    (16, '2020-01-02 15:00:00'),
    (16, '2020-01-02 16:00:00'),
    (16, '2020-01-02 17:00:00'),

])
@pytest.mark.parametrize("tech", [1, 2, 8, 12])
def test_dispatch(solution, benchmark, zone, time, tech):
    '''Assert solution dispatch decisions match known value'''
    assert value(solution.gen_disp[zone, tech, time]) \
        == pytest.approx(value(benchmark.gen_disp[zone, tech, time]))


@pytest.mark.parametrize("zone,time", [
    (9, '2020-01-03 03:00:00'),
    (9, '2020-01-03 04:00:00'),
    (9, '2020-01-03 05:00:00'),
    (9, '2020-01-04 23:00:00'),
])
@pytest.mark.parametrize("tech", [15])
def test_storage(solution, benchmark, zone, time, tech):
    '''Assert solution storage charge decisions match known value'''
    assert value(solution.stor_charge[zone, tech, time]) \
        == pytest.approx(value(benchmark.stor_charge[zone, tech, time]))


@pytest.mark.parametrize("zone,time", [
    (16, '2020-01-03 10:00:00'),
    (16, '2020-01-03 11:00:00'),
    (16, '2020-01-03 12:00:00'),
])
@pytest.mark.parametrize("tech", [13])
def test_hybrid(solution, benchmark, zone, time, tech):
    '''Assert hybrid dispatch solutions match known value'''
    assert value(solution.hyb_disp[zone, tech, time]) \
        == pytest.approx(value(benchmark.hyb_disp[zone, tech, time]), abs=1e-11)


@pytest.mark.parametrize("tfrom,tto,time", [
    (4, 5, '2020-01-02 14:00:00'),
    (4, 5, '2020-01-02 15:00:00'),
    (4, 5, '2020-01-02 16:00:00'),
    (4, 5, '2020-01-02 17:00:00'),
])
def test_transmission(solution, benchmark, tfrom, tto, time):
    '''Assert transmission decisions match known value'''
    assert value(solution.intercon_disp[tfrom, tto, time])\
        == value(benchmark.intercon_disp[tfrom, tto, time])


def test_problemsize(solution, benchmark):
    '''Asssert solution problem size matches known value'''
    assert solution.nobjectives() == benchmark.nobjectives()
    assert solution.nvariables() == benchmark.nvariables()
    assert solution.nconstraints() == benchmark.nconstraints()


def test_objective(solution, benchmark):
    '''Assert solution objective matches known value'''
    assert value(solution.Obj) == pytest.approx(value(benchmark.Obj))

# DONE access values above from yaml or pickle file instead of hardcoded here
