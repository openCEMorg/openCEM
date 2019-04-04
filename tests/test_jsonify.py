import json

from cemo.jsonify import jsoninit


def test_json_init(solution):
    data = jsoninit(solution)
    # with open('tests/jsoninit_test.json', 'w') as f:
    #    json.dump(data, f, indent=2)
    with open('tests/jsoninit_test.json', 'r') as f1:
        data2 = json.load(f1)
    assert json.dumps(data) == json.dumps(data2)
