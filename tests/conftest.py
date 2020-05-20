'''Common fixtures for test suite'''
import pickle
from pathlib import Path
import pytest
import tempfile
import shutil
import gzip
from pyomo.environ import DataPortal
from pyomo.opt import SolverFactory

from cemo.model import CreateModel, model_options


@pytest.fixture(scope="session")
def model_options_fixture():
    '''Model options fixture for tests'''
    options2 = model_options(nem_emit_limit=True)
    return options2


@pytest.fixture(scope="session",
                params=[
                    'CTV_trans',
                ])
def model(request):
    '''Model fixture for tests, returns an openCEM model'''
    options = model_options(unslim=True,
                            nem_emit_limit=True,
                            nem_disp_ratio=True,
                            nem_re_disp_ratio=True,
                            nem_ret_ratio=True,
                            nem_ret_gwh=True,
                            region_ret_ratio=True)
    return CreateModel(request.param, options).create_model()


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
    parser.addoption(
        "--runslow", action="store_true", default=False, help="run slow tests"
    )


def pytest_configure(config):
    config.addinivalue_line("markers", "slow: mark test as slow to run")


def pytest_collection_modifyitems(config, items):
    if config.getoption("--runslow"):
        # --runslow given in cli: do not skip slow tests
        return
    skip_slow = pytest.mark.skip(reason="need --runslow option to run")
    for item in items:
        if "slow" in item.keywords:
            item.add_marker(skip_slow)


@pytest.fixture(scope="session")
def solution(request, instance):
    '''Solution fixture is an instance solved on the spot using local solver'''
    solver = request.config.getoption("--solver")
    sol = SolverFactory(solver)
    assert sol.solve(instance)
    return instance


@pytest.fixture(scope="session")
def inst_lite():
    '''Model instance with full year NEM wide sets and input parameters only'''
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp:
        shutil.copyfileobj(gzip.open('tests/inst_lite_data.json.gz'), tmp)
        options = model_options(nem_emit_limit=True, nem_ret_ratio=True, nem_ret_gwh=True)
        model = CreateModel('lite', options).create_model(test=True)
        data = DataPortal()
        data.load(filename=tmp.name)
        return model.create_instance(data)


@pytest.fixture()
def delete_sim2025_dat():
    '''Fixture to delete temporary file Sim2025.dat

    This is an inconvenient teardown step but enables the most
    accurate test of template generation, using filecmp'''
    yield
    Path('Sim2025.dat').unlink()
