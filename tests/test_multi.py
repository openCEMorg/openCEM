# Multi year simulation unit tests
import filecmp
import json
from difflib import SequenceMatcher

import pytest

from cemo.multi import SolveTemplate


def test_multi_conf_file_not_found():
    ''' Fail if file does not exist'''
    with pytest.raises(FileNotFoundError):
        SolveTemplate(cfgfile='Nofile.cfg')


def test_multi_bad_nemret():
    ''' Assert validate bad nemret'''
    with pytest.raises(ValueError):
        SolveTemplate(cfgfile='tests/MultiBad.cfg')


def test_multi_template_first():
    '''Tests generate first year template by comparing to known good result'''
    X = SolveTemplate(cfgfile='tests/Sample.cfg')
    X.generateyeartemplate(X.Years[0], test=True)
    assert filecmp.cmp(X.tmpdir + 'Sim2020.dat', 'tests/Sim2020.dat')


def test_multi_template_second():
    '''Tests generate second (and later) year template by comparing to known good result'''
    X = SolveTemplate(cfgfile='tests/Sample.cfg')
    X.generateyeartemplate(X.Years[1], test=True)
    with open(X.tmpdir + '/Sim2025.dat') as ff:
        fromfile = ff.readlines()
    with open('tests/Sim2025.dat') as tf:
        tofile = tf.readlines()
    # Check that they are mostly the same, but for gen_cap_initial tmpdir line
    d = SequenceMatcher(None, fromfile, tofile)
    assert d.ratio() >= 0.996


def test_multi_metadata():
    '''Tests generate year template by comparing to known good result'''
    X = SolveTemplate(cfgfile='tests/Sample.cfg')
    meta = X.generate_metadata()
    with open('tests/metadata.json', 'r') as f:
        metad = json.load(f)
    assert meta == metad
