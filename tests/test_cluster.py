'''Test suite for cluster module'''
# pylint: disable=protected-access
from difflib import SequenceMatcher

import datetime
import pytest

import cemo.cluster
from cemo.cluster import next_weekday, prev_weekday


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


def test_cluster_data_files(model_options):
    '''Assert generated scenario files match a known good value'''
    clus = cemo.cluster.CSVCluster(max_d=6)
    test_cluster = cemo.cluster.ClusterRun(
        clus, 'tests/CNEM.template', model_options)
    test_cluster._gen_dat_files()
    with open(test_cluster.tmpdir + '/S5.dat') as source:
        fromfile = source.readlines()
    with open('tests/CNEM5test.dat') as test:
        tofile = test.readlines()
    # Check that they are mostly the same, but for gen_cap_initial tmpdir line
    sequence = SequenceMatcher(None, fromfile, tofile)
    assert sequence.ratio() >= 1


def test_cluster_scenario_structure(model_options):
    '''Assert generated scenario tree structure matches a good known value'''
    clus = cemo.cluster.CSVCluster(max_d=6)
    test_cluster = cemo.cluster.ClusterRun(
        clus, 'tests/CNEM.template', model_options)
    test_cluster._gen_scen_struct()
    with open(test_cluster.tmpdir + '/ScenarioStructure.dat') as source:
        fromfile = source.readlines()
    with open('tests/ScenTest.dat') as test:
        tofile = test.readlines()
    # Check that they are mostly the same
    sequence = SequenceMatcher(None, fromfile, tofile)
    assert sequence.ratio() >= 1


def test_cluster_gen_ref_model(model_options):
    '''Assert reference model is being generated as a good known value'''
    clus = cemo.cluster.CSVCluster()
    test_cluster = cemo.cluster.ClusterRun(
        clus, 'tests/CNEM.template', model_options)
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


def test_cluster_prev_weekday():
    '''assert prev_weekday works as intended'''
    assert prev_weekday(datetime.date(2019, 4, 2), 2) == datetime.date(2019, 3, 27)
    assert prev_weekday(datetime.date(2019, 4, 2), 0) == datetime.date(2019, 4, 1)
