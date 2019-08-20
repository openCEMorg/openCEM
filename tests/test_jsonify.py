'''Test suite for jsonify module'''

import json

from cemo.jsonify import json_readr, json_readr_meta, json_readr_year, jsoninit


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
    data = jsoninit(solution, 2020)
    with open('tests/jsoninit_test.json', 'r') as known:
        data2 = json.load(known)
    for key in data:
        assert dumped_data(data[key]) == dumped_data(data2[key])


def test_json_readr():
    '''Assert that a one per line openCEM JSON file reads as a conventional dictionary'''
    with open('tests/test_reading.json') as known:
        full_data = json.load(known)
    assert full_data == json_readr('tests/test_reader_one_per_line.json')


def test_json_readr_meta():
    '''Assert that a one per line openCEM JSON file reads metadata'''
    with open('tests/test_reading.json') as known:
        full_data = json.load(known)
    assert {
        "meta": full_data['meta']
    } == json_readr_meta('tests/test_reader_one_per_line.json')


def test_json_readr_year():
    '''Assert that a one per line openCEM JSON file reads metadata'''
    with open('tests/test_reading.json') as known:
        full_data = json.load(known)
    assert {
        "2025": full_data['2025']
    } == json_readr_year('tests/test_reader_one_per_line.json', 2025)
