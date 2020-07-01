'''Test suite for jsonify module'''

import json

from cemo.jsonify import (json_readr, json_readr_meta, json_readr_year,
                          jsoninit, jsonify, json_carry_forward_cap, jsonopcap0)


def sort_func(item):
    '''Sort list of dictionaries by index'''
    if isinstance(item, dict):
        return item['index']
    return item


def dumped_data(entry):
    '''Return sorted list of dicts for entry, and convert list to tuples in entry items'''
    if isinstance(entry, list):
        if all(isinstance(n, list) for n in entry):
            entry = [tuple(i) for i in entry]
        if all(isinstance(n, dict) and 'index' in n for n in entry):
            entry = [{
                "index": tuple(i['index']) if isinstance(i['index'], list) else i['index'],
                "value": round(i['value'], 3) if not isinstance(i['value'], list) else i['value']
            } for i in entry]
        return sorted(entry, key=sort_func)
    if isinstance(entry, dict):
        if all(isinstance(entry[n], list) for n in entry):
            return {i: sorted(entry[i], key=sort_func) for i in entry}
        if all(isinstance(n, int) for n in entry.keys()):
            return {str(i): entry[i] for i in entry}
    return entry


def test_json_init(solution):
    '''Assert that generated jsoninit of solution matches known output'''
    data = jsoninit(solution, 2020)
    with open('tests/jsoninit_test.json', 'r') as known:
        data2 = json.load(known)
    for key in data:
        assert dumped_data(data[key]) == dumped_data(data2[key])


def test_json_carry_fwd_cap(solution):
    '''Assert carry forward cap matches known output'''
    data = json_carry_forward_cap(solution)
    with open('tests/jsoncarryfwd_test.json') as known:
        data2 = json.load(known)
    for key in data:
        assert dumped_data(data[key]) == dumped_data(data2[key])


def test_jsonopcap0(solution):
    '''Assert jsonopcap0 matches known output'''
    data = jsonopcap0(solution)
    with open('tests/jsonopcap0_test.json') as known:
        data2 = json.load(known)
    for key in data:
        assert dumped_data(data[key]) == dumped_data(data2[key])


def test_jsonify_sol(solution):
    '''Assert that generated jsonify of solution matches known output

    There are multiple types of data in jsonify and they need to be handled'''
    data = jsonify(solution, '2020')
    with open('tests/jsonify_test.json', 'r') as known:
        data2 = json.load(known)
    for bunch in data['2020']:
        try:
            for key in data['2020'][bunch]:
                assert dumped_data(data['2020'][bunch][key]) == dumped_data(
                    data2['2020'][bunch][key])
        except TypeError:
            # Objective bunch has a single entry, a float
            assert dumped_data(data['2020'][bunch]) == dumped_data(
                data2['2020'][bunch])


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
