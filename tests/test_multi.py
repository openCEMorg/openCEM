# Multi year simulation unit tests
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
