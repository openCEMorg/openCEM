'''Test suite for utils module'''
import pytest

from cemo.utils import printstats
from cemo.rules import region_in_zone


def test_printstats(request, solution, capfd):
    '''Assert that solution stats printout matches known value'''
    printstats(solution)
    captured = capfd.readouterr()
    if request.config.getoption("--solver") == 'cbc':
        testfile = 'tests/stats_cbc.txt'
    else:
        testfile = 'tests/stats.txt'
    with open(testfile, 'r') as sample:
        array = sample.read()
    assert captured.out == array


@pytest.mark.parametrize("zone,result", [
    (6, 1),  # CAN in NSW
    (2, 2),  # CQ in QLD
    (13, 3),  # NSA in SA
    (16, 4),  # TAS in TAS
    (9, 5),  # LV in VIC
])
def test_region_in_zone(zone, result):
    '''Assert correct region is returned for a given zone'''
    assert result == pytest.approx(region_in_zone(zone))
