from cemo.utils import printstats


def test_printstats(solution, capfd):
    printstats(solution)
    captured = capfd.readouterr()
    f = open('tests/stats.txt', 'r')
    assert captured.out == f.read()
