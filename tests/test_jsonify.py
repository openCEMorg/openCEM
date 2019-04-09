'''Test suite for jsonify module'''

import json

from cemo.jsonify import jsoninit


def sort_func(entry):
    '''Sort list of dictionaries by index'''
    if not isinstance(entry, int):
        if isinstance(entry, dict):
            return entry['index']
    return entry


def dumped_data(entry):
    '''create sorted dumps of dictionary'''
    if not isinstance(entry, (int, float, str)):
        return json.dumps(sorted(entry, key=sort_func))
    return json.dumps(entry)


def test_json_init(solution):
    '''Assert that generated jsoninit of solution matches known output'''
    data = jsoninit(solution)
    with open('tests/jsoninit_test.json', 'r') as known:
        data2 = json.load(known)
    for key in data:
        assert dumped_data(data[key]) == dumped_data(data2[key])
