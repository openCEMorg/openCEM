# Common fixtures for test suite
import pytest
import pickle
from cemo.core import create_model
from pyomo.opt import SolverFactory
from pyomo.environ import DataPortal
# IDEA maybe we should have a NEM wide test


@pytest.fixture(scope="session",
                params=[
                    'CTV_trans',
                ])
def model(request):
    return create_model(request.param, unslim=True, emitlimit=True, nemret=True)


@pytest.fixture(scope="session")
def instance(model):
    DataPath = 'tests/' + model.name + '.json'
    data = DataPortal()
    data.load(filename=DataPath)
    return model.create_instance(data)


@pytest.fixture
def benchmark(instance):
    pickledDataPath = 'tests/' + instance.name + '.p'
    return pickle.load(open(pickledDataPath, "rb"))


def pytest_addoption(parser):
    parser.addoption(
        "--solver",
        action="store",
        default="cbc",
        help="Specify Pyomo solver"
    )


@pytest.fixture(scope="session")
def solution(request, instance):
    solver = request.config.getoption("--solver")
    sol = SolverFactory(solver)
    assert sol.solve(instance)
    return instance


@pytest.fixture(scope="session")
def temp_data_dir(tmpdir_factory):
    return tmpdir_factory.mktemp("CEMOtemp")
