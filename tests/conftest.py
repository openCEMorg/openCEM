# Common fixtures for test suite
import pytest
import pickle
from cemo.cemo import create_model
from pyomo.opt import SolverFactory


@pytest.fixture(params=[
    'CEMO_testTASVIC',
])
def model(request):
    return create_model(request.param)


@pytest.fixture
def instance(model):
    DataPath = 'tests/' + model.name + '.dat'
    return model.create_instance(DataPath)


@pytest.fixture
def benchmark(instance):
    pickledDataPath = 'tests/' + instance.name + '.p'
    return pickle.load(open(pickledDataPath, "rb"))


def pytest_addoption(parser):
    parser.addoption(
        "--solver", action="store", default="cbc", help="Specify Pyomo solver"
    )


@pytest.fixture
def solver(request):
    sol = request.config.getoption("--solver")
    return SolverFactory(sol)


@pytest.fixture
def solution(solver, instance):
    solver.solve(instance)
    instance.compute_statistics()
    return instance
