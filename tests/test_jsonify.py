import json

from cemo.jsonify import jsoninit

def sort_func(x):
    if type(x) is not int:
        if type(x)==dict:
            return x['index']
    return x

def dumped_data(x):
    if type(x) not in [int,float,str]:
        return json.dumps(sorted(x,key=sort_func))
    return json.dumps(x)

def test_json_init(solution):
    data = jsoninit(solution)
    with open('jsoninit_test.json', 'w') as f:
        json.dump(data, f, indent=2)
    with open('tests/jsoninit_test.json', 'r') as f1:
        data2 = json.load(f1)
    for key in data.keys():
        print(key)
        assert dumped_data(data[key])==dumped_data(data2[key])

