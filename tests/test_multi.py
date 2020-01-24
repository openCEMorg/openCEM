'''Unit test suite for multi.py module (multi year simulations)'''
import filecmp
import json
import tempfile

import pytest

from cemo.multi import SolveTemplate, sql_tech_pairs, sql_list, roundup


@pytest.mark.parametrize(
    "value,result",
    [({1: [1, 3, 5]}, '((1, 1), (1, 3), (1, 5))'),
     ({}, '((99, 99))'),
     ])
def test_sql_tech_pairs(value, result):
    '''Test behaviour of sql_tech_pairs'''
    assert sql_tech_pairs(value) == result


@pytest.mark.parametrize(
    "value,result",
    [([1, 3, 5], '1, 3, 5'),
     ([], '99'),
     ])
def test_sql_list(value, result):
    '''Test behaviour of sql_list'''
    assert sql_list(value) == result


def test_roundup():
    '''Test behaviour of roundup cap'''
    assert roundup(-1e-7) == 0
    assert roundup(-1e-5) == -1e-5
    assert roundup(1344) == 1344


def test_multi_conf_file_not_found():
    ''' Fail if file does not exist'''
    with pytest.raises(FileNotFoundError):
        SolveTemplate(cfgfile='Nofile.cfg')


@pytest.mark.parametrize(
    "option,value",
    [('nem_ret_ratio', 'nem_ret_ratio = [0.1, 1.2, 0.3, 0.4, 0.5, 0.6]'),
     ('nem_ret_gwh', 'nem_ret_gwh = [45222, 150000, -12, a, 14]'),
     ('region_ret_ratio',
      'region_ret_ratio = [[1, [0.1, 1.2, 0.3, 0.4, 0.5, 0.6]]]'),
     ('region_ret_ratio',
      'region_ret_ratio = [[2, [ 0.2, 0.3, 0.4, 0.5, 0.6]]]'),
     ('nem_emit_limit', 'nem_emit_limit = [-100, 100, 100, 100, 100, 100]'),
     ('Years', 'Years=[2020,2022,2071]'), ('discountrate', 'discountrate=1.1'),
     ('cost_emit', 'cost_emit = [-11,2,3,4,5,6,8]'),
     ('nem_disp_ratio', 'nem_disp_ratio=[0,0,0,2,0,0,0]'),
     ('nem_re_disp_ratio', 'nem_re_disp_ratio=[0,0,0,0,0,0]')])
def test_multi_bad_cfg(option, value):
    ''' Assert validate bad config option by replacing known bad options in sample file'''
    with open('tests/Sample.cfg') as sample:
        with tempfile.NamedTemporaryFile(
                mode='w', delete=False) as temp_sample:
            for line in sample:
                if option in line:
                    line = value + '\n'
                temp_sample.write(line)
                temp_sample.flush()
            with pytest.raises(ValueError):
                SolveTemplate(cfgfile=temp_sample.name)


@pytest.mark.parametrize("option,value", [
    ('custom_costs', 'custom_costs=Badfile.csv'),
    ('exogenous_capacity', 'exogenous_capacity=Badfile.csv'),
    ('Template', 'Template=Badfile.dat'),
])
def test_multi_bad_file(option, value):
    ''' Assert that multi detects missing files in config'''
    with open('tests/Sample.cfg') as sample:
        with tempfile.NamedTemporaryFile(
                mode='w', delete=False) as temp_sample:
            for line in sample:
                if option in line:
                    line = value + '\n'
                temp_sample.write(line)
            temp_sample.flush()
            with pytest.raises(OSError):
                SolveTemplate(cfgfile=temp_sample.name)


def test_multi_template_first():
    '''Tests generate first year template by comparing to known good result'''
    multi_sim = SolveTemplate(cfgfile='tests/Sample.cfg')
    multi_sim.generateyeartemplate(multi_sim.Years[0], test=True)
    assert filecmp.cmp(multi_sim.tmpdir + 'Sim2020.dat', 'tests/Sim2020.dat')


def test_multi_template_second(delete_sim2025_dat):
    '''Tests generate second (and later) year template by comparing to known good result'''
    multi_sim = SolveTemplate(cfgfile='tests/Sample.cfg', tmpdir='')
    multi_sim.generateyeartemplate(multi_sim.Years[1], test=True)
    assert filecmp.cmp(multi_sim.tmpdir + 'Sim2025.dat', 'tests/Sim2025.dat')


def test_multi_metadata():
    '''Tests generate year template by comparing to known good result'''
    multi_sim = SolveTemplate(cfgfile='tests/Sample.cfg')
    meta = multi_sim.generate_metadata()
    with open('tests/metadata.json', 'r') as test_meta:
        metad = json.load(test_meta)
    assert json.dumps(meta, indent=2) == json.dumps(metad, indent=2)
