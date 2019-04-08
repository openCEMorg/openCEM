# Multi year simulation unit tests
import filecmp
import json
import tempfile
from difflib import SequenceMatcher

import pytest

from cemo.multi import SolveTemplate


def test_multi_conf_file_not_found():
    ''' Fail if file does not exist'''
    with pytest.raises(FileNotFoundError):
        SolveTemplate(cfgfile='Nofile.cfg')


@pytest.mark.parametrize("option,value", [
    ('nem_ret_ratio', 'nem_ret_ratio = [0.1, 1.2, 0.3, 0.4, 0.5, 0.6]'),
    ('nem_ret_gwh', 'nem_ret_gwh = [45222, 150000, -12, a, 14]'),
    ('region_ret_ratio', 'region_ret_ratio = [[1, [0.1, 1.2, 0.3, 0.4, 0.5, 0.6]]]'),
    ('region_ret_ratio', 'region_ret_ratio = [[2, [ 0.2, 0.3, 0.4, 0.5, 0.6]]]'),
    ('emitlimit', 'emitlimit = [-100, 100, 100, 100, 100, 100]'),
    ('Years', 'Years=[2020,2022,2071]'),
    ('discountrate', 'discountrate=1.1'),
    ('cost_emit', 'cost_emit = [-11,2,3,4,5,6,8]'),
    ('nem_disp_ratio', 'nem_disp_ratio=[0,0,0,2,0,0,0]'),
    ('nem_re_disp_ratio', 'nem_re_disp_ratio=[0,0,0,0,0,0]')
]
)
def test_multi_bad_cfg(option, value):
    ''' Assert validate bad config option'''
    fp = tempfile.NamedTemporaryFile()
    with open('tests/Sample.cfg') as fin:
        with open(fp.name, 'w') as fo:
            for line in fin:
                if option in line:
                    line = value + '\n'
                fo.write(line)
    with pytest.raises(ValueError):
        SolveTemplate(cfgfile=fp.name)


@pytest.mark.parametrize("option,value", [
    ('custom_costs', 'custom_costs=Badfile.csv'),
    ('exogenous_capacity', 'exogenous_capacity=Badfile.csv'),
    ('Template', 'Template=Badfile.dat'),
])
def test_multi_bad_file(option, value):
    ''' Assert validate bad config option'''
    fp = tempfile.NamedTemporaryFile()
    with open('tests/Sample.cfg') as fin:
        with open(fp.name, 'w') as fo:
            for line in fin:
                if option in line:
                    line = value + '\n'
                fo.write(line)
    with pytest.raises(OSError):
        SolveTemplate(cfgfile=fp.name)


def test_multi_template_first():
    '''Tests generate first year template by comparing to known good result'''
    X = SolveTemplate(cfgfile='tests/Sample.cfg')
    X.generateyeartemplate(X.Years[0], test=True)
    assert filecmp.cmp(X.tmpdir + 'Sim2020.dat', 'tests/Sim2020.dat')


def test_multi_template_second():
    '''Tests generate second (and later) year template by comparing to known good result'''
    X = SolveTemplate(cfgfile='tests/Sample.cfg')
    X.generateyeartemplate(X.Years[1], test=True)
    with open(X.tmpdir + 'Sim2025.dat') as ff:
        fromfile = ff.readlines()
    with open('tests/Sim2025.dat') as tf:
        tofile = tf.readlines()
    # Check that they are mostly the same, but for tempdir entries
    d = SequenceMatcher(None, fromfile, tofile)
    assert d.ratio() >= 0.99657534


def test_multi_metadata():
    '''Tests generate year template by comparing to known good result'''
    X = SolveTemplate(cfgfile='tests/Sample.cfg')
    meta = X.generate_metadata()
    with open('tests/metadata.json', 'r') as f:
        metad = json.load(f)
    assert json.dumps(meta, indent=2) == json.dumps(metad, indent=2)
