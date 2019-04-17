'''Test suite for utils module'''
from cemo.utils import printstats


def test_printstats(solution, capfd):
    '''Assert that solution stats printout matches known value'''
    printstats(solution)
    captured = capfd.readouterr()
    with open('tests/stats.txt', 'r') as sample:
        array = sample.read()
    assert captured.out == array
