import filecmp
from difflib import SequenceMatcher

import pytest

import cemo.cluster


def test_cluster_instantiation():
    assert cemo.cluster.CSVCluster()


@pytest.mark.parametrize("cluster_no", [
    3,
    6,
    9,
])
def test_cluster_size(cluster_no):
    a = cemo.cluster.CSVCluster()
    a.clusterset(cluster_no)
    assert a.Xcluster.size == cluster_no * 3


# TODO make a separate test suite for cluster run


def test_cluster_data_files():
    clus = cemo.cluster.CSVCluster(max_d=6)
    a = cemo.cluster.ClusterRun(
        clus, 'tests/CNEM.template', emitlimit=True)
    a._gen_dat_files()
    with open(a.tmpdir + '/S5.dat') as ff:
        fromfile = ff.readlines()
    with open('tests/CNEM5test.dat') as tf:
        tofile = tf.readlines()
    # Check that they are mostly the same, but for gen_cap_initial tmpdir line
    d = SequenceMatcher(None, fromfile, tofile)
    assert d.ratio() >= 0.994


def test_cluster_gen_scenario_struct():
    clus = cemo.cluster.CSVCluster(max_d=6)
    a = cemo.cluster.ClusterRun(
        clus, 'tests/CNEM.template', emitlimit=True)
    a._gen_scen_struct()
    assert filecmp.cmp(a.tmpdir + '/ScenarioStructure.dat',
                       'tests/ScenTest.dat')


def test_cluster_gen_ref_model(temp_data_dir):
    clus = cemo.cluster.CSVCluster()
    a = cemo.cluster.ClusterRun(
        clus, 'tests/CNEM.template', emitlimit=True)
    a._gen_ref_model()
    assert filecmp.cmp(a.tmpdir + '/ReferenceModel.py',
                       'tests/ReferenceModel.py')
