'''Common fixtures for test suite'''
import pickle

import pytest
from pyomo.opt import SolverFactory

from cemo.model import create_model


@pytest.fixture(scope="session",
                params=[
                    'CTV_trans',
                ])
def model(request):
    '''Model fixture for tests, returns an openCEM model'''
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
    '''Model options fixture for tests'''
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
    '''Model instance fixture based on model fixture'''
    data = 'tests/' + model.name + '.dat'
    return model.create_instance(data)


@pytest.fixture
def benchmark(instance):
    '''Benchmark fixture for tests is a solved model instance
    stored as a pickled form'''
    pickledDataPath = 'tests/' + instance.name + '.p'
    return pickle.load(open(pickledDataPath, "rb"))


def pytest_addoption(parser):
    '''Solver options for solution fixture'''
    parser.addoption(
        "--solver",
        action="store",
        default="cbc",
        help="Specify Pyomo solver"
    )


@pytest.fixture(scope="session")
def solution(request, instance):
    '''Solution fixture is an instance solved on the spot using local solver'''
    solver = request.config.getoption("--solver")
    sol = SolverFactory(solver)
    assert sol.solve(instance)
    return instance


@pytest.fixture(scope="session")
def temp_data_dir(tmpdir_factory):
    '''Temporary data directory fixture for tests'''
    return tmpdir_factory.mktemp("CEMOtemp")
