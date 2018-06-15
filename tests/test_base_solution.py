import pytest

from pyomo.environ import value


def test_solver(solver, instance):
    assert solver.solve(instance)


@pytest.mark.parametrize("zone,tech,inv", [
    (16, 1, 2020),
    (16, 2, 2020),
    (16, 8, 2020),
    (16, 12, 2020),
])
def test_capacities(solution, benchmark, zone, tech, inv):
    assert value(solution.NewCap[zone, tech, inv]) \
        == value(benchmark.NewCap[zone, tech, inv])


def test_problemsize(solution, benchmark):
    assert solution.nobjectives() == benchmark.nobjectives()
    assert solution.nvariables() == benchmark.nvariables()
    assert solution.nconstraints() == benchmark.nconstraints()


def test_objective(solution, benchmark):
    assert pytest.approx(value(solution.Obj) == value(benchmark.Obj))

# TODO access values above from yaml file instead of hardcoded here
