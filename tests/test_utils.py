from cemo.utils import printstats


def test_printstats(solution, capfd):
    printstats(solution)
    captured = capfd.readouterr()
    with open('tests/stats.txt', 'r') as ins:
        array = ''
        for line in ins:
            array += line
    assert captured.out == array
