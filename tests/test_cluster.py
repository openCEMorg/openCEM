'''Test suite for cluster module'''
# pylint: disable=protected-access
from difflib import SequenceMatcher

import datetime
import pytest

import cemo.cluster
from cemo.cluster import next_weekday, prev_weekday
from cemo.utils import plotcluster


def test_cluster_instantiation():
    '''Assert cluster instantiates correctly'''
    assert cemo.cluster.CSVCluster()


@pytest.mark.parametrize("cluster_no", [
    3,
    6,
    9,
])
def test_cluster_size(cluster_no):
    '''Assert cluster sizes on request'''
    test_cluster = cemo.cluster.CSVCluster()
    test_cluster.clusterset(cluster_no)
    assert test_cluster.Xcluster.size == cluster_no * 3


def test_cluster_data_files(model_options_fixture):
    '''Assert generated scenario files match a known good value'''
    clus = cemo.cluster.CSVCluster(max_d=6)
    test_cluster = cemo.cluster.ClusterRun(
        clus, 'tests/CNEM.template', model_options_fixture)
    test_cluster._gen_dat_files()
    with open(test_cluster.tmpdir + '/S5.dat') as source:
        fromfile = source.readlines()
    with open('tests/CNEM5test.dat') as test:
        tofile = test.readlines()
    # Check that they are mostly the same, but for gen_cap_initial tmpdir line
    sequence = SequenceMatcher(None, fromfile, tofile)
    assert sequence.ratio() >= 1


def test_cluster_scenario_structure(model_options_fixture):
    '''Assert generated scenario tree structure matches a good known value'''
    clus = cemo.cluster.CSVCluster(max_d=6)
    test_cluster = cemo.cluster.ClusterRun(
        clus, 'tests/CNEM.template', model_options_fixture)
    test_cluster._gen_scen_struct()
    with open(test_cluster.tmpdir + '/ScenarioStructure.dat') as source:
        fromfile = source.readlines()
    with open('tests/ScenTest.dat') as test:
        tofile = test.readlines()
    # Check that they are mostly the same
    sequence = SequenceMatcher(None, fromfile, tofile)
    assert sequence.ratio() >= 1


def test_cluster_gen_ref_model(model_options_fixture):
    '''Assert reference model is being generated as a good known value'''
    clus = cemo.cluster.CSVCluster()
    test_cluster = cemo.cluster.ClusterRun(
        clus, 'tests/CNEM.template', model_options_fixture)
    test_cluster._gen_ref_model()
    with open(test_cluster.tmpdir + '/ReferenceModel.py') as source:
        fromfile = source.readlines()
    with open('tests/ReferenceModel.py') as test:
        tofile = test.readlines()
    # Check that they are mostly the same
    sequence = SequenceMatcher(None, fromfile, tofile)
    assert sequence.ratio() >= 1


def test_cluster_next_weekday():
    '''assert next_weekday works as intended'''
    assert next_weekday(datetime.date(2019, 4, 2), 2) == datetime.date(2019, 4, 3)
    assert next_weekday(datetime.date(2019, 4, 2), 0) == datetime.date(2019, 4, 8)
    assert next_weekday(datetime.date(2019, 4, 2), 6) == datetime.date(2019, 4, 7)


def test_cluster_prev_weekday():
    '''assert prev_weekday works as intended'''
    assert prev_weekday(datetime.date(2019, 4, 2), 2) == datetime.date(2019, 3, 27)
    assert prev_weekday(datetime.date(2019, 4, 2), 0) == datetime.date(2019, 4, 1)


def test_csv_cluster_missing_file():
    '''Test that CSV cluster detects missing file'''
    with pytest.raises(SystemExit):
        cemo.cluster.CSVCluster(source='nosource.csv')


def test_append_to_cluster():
    '''Test append to cluster method'''
    cluster = cemo.cluster.CSVCluster(max_d=6)
    injected_week = '2019-07-07'
    cluster.append_to_cluster(injected_week)
    repr = """Cluster Data generator
    week       date    weight
0    40 2020-04-03  0.411765
1    25 2019-12-20  0.058824
2    11 2019-09-13  0.431373
3    31 2020-01-31  0.039216
4    29 2020-01-17  0.019608
5    28 2020-01-10  0.019608
6    52 2019-07-07  0.019608"""
    assert cluster.__repr__() == repr


@pytest.mark.slow
def test_dunkelflaute(inst_lite):
    '''Test Dark calm week algorithm detection'''
    cluster = cemo.cluster.InstanceCluster(inst_lite, max_d=6)
    assert cluster.dunkelflaute_week() == '2035-06-02'
    # assert cluster.dunkelflaute_week(summer=True) == '2035-01-30'


@pytest.mark.slow
def test_systempeak(inst_lite):
    '''Test Dark calm week algorithm detection'''
    cluster = cemo.cluster.InstanceCluster(inst_lite, max_d=6)
    print(cluster)
    assert cluster.system_peak_week() == '2035-01-16'


@pytest.mark.slow
def test_plot_cluster(inst_lite):
    '''Test cluster plotting function'''
    cluster = cemo.cluster.InstanceCluster(inst_lite, max_d=6)
    plt = plotcluster(cluster, row=2, col=3, ylim=(0, 14000))
    assert plt.gcf().number == 1
