# Common fixtures for test suite
import pickle

import pytest
from pyomo.opt import SolverFactory

from cemo.model import create_model


@pytest.fixture(scope="session",
                params=[
                    'CTV_trans',
                ])
def model(request):
    return create_model(request.param,
                        unslim=True,
                        emitlimit=True,
                        nem_disp_ratio=True,
                        nem_re_disp_ratio=True,
                        nem_ret_ratio=True,
                        nem_ret_gwh=True,
                        region_ret_ratio=True)


@pytest.fixture(scope="session")
def model_options():
    options = {}
    options.update({'emitlimit': True})
    options.update({'nem_ret_gwh': False})
    options.update({'nem_ret_ratio': False})
    options.update({'region_ret_ratio': False})
    options.update({'nem_disp_ratio': False})
    options.update({'nem_re_disp_ratio': False})
    return options


@pytest.fixture(scope="session")
def instance(model):
    data = 'tests/' + model.name + '.dat'
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
