'''Test suite for cluster module'''
from difflib import SequenceMatcher

import pytest

import cemo.cluster


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
    a = cemo.cluster.CSVCluster()
    a.clusterset(cluster_no)
    assert a.Xcluster.size == cluster_no * 3


def test_cluster_data_files(model_options):
    '''Assert generated scenario files match a known good value'''
    clus = cemo.cluster.CSVCluster(max_d=6)
    a = cemo.cluster.ClusterRun(clus, 'tests/CNEM.template', model_options)
    a._gen_dat_files()
    with open(a.tmpdir + '/S5.dat') as ff:
        fromfile = ff.readlines()
    with open('tests/CNEM5test.dat') as tf:
        tofile = tf.readlines()
    # Check that they are mostly the same, but for gen_cap_initial tmpdir line
    d = SequenceMatcher(None, fromfile, tofile)
    assert d.ratio() >= 0.994


def test_cluster_gen_scenario_struct(model_options):
    '''Assert generated scenario tree structure matches a good known value'''
    clus = cemo.cluster.CSVCluster(max_d=6)
    a = cemo.cluster.ClusterRun(clus, 'tests/CNEM.template', model_options)
    a._gen_scen_struct()
    with open(a.tmpdir + '/ScenarioStructure.dat') as ff:
        fromfile = ff.readlines()
    with open('tests/ScenTest.dat') as tf:
        tofile = tf.readlines()
    # Check that they are mostly the same
    d = SequenceMatcher(None, fromfile, tofile)
    assert d.ratio() >= 0.99999999


def test_cluster_gen_ref_model(temp_data_dir, model_options):
    clus = cemo.cluster.CSVCluster()
    a = cemo.cluster.ClusterRun(clus, 'tests/CNEM.template', model_options)
    a._gen_ref_model()
    with open(a.tmpdir + '/ReferenceModel.py') as ff:
        fromfile = ff.readlines()
    with open('tests/ReferenceModel.py') as tf:
        tofile = tf.readlines()
    # Check that they are mostly the same
    d = SequenceMatcher(None, fromfile, tofile)
    assert d.ratio() >= 0.999999999999
