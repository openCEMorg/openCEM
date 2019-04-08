from cemo.utils import printstats


def test_printstats(solution, capfd):
    printstats(solution)
    captured = capfd.readouterr()
    with open('tests/stats.txt', 'r') as f:
        array = f.read()
    assert captured.out == array
