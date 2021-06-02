"""Test suite for parquetify module"""
import pandas as pd
from cemo.parquetify import parquetify
from cemo.summary import Summary
import pytest
import shutil


def test_parquetify(solution):
    """Test that the entire variable map of an instance is saved

    Data is saved to a temporary directory and sample data tested
    Directory is removed before asserts"""
    parquetify(solution, 'tmptest', 2022)
    gen_disp = pd.read_parquet('tmptest/2022/disp')
    gen_cap_op = pd.read_parquet('tmptest/2022/cap_op')
    srmc = pd.read_parquet('tmptest/2022/srmc')
    # Cheeky summary test here
    [cdu, sum] = Summary('tmptest', [2022], cache=False).get_summary()
    shutil.rmtree('tmptest', ignore_errors=True)
    assert gen_disp.query(
        "zone==9 & tech==6 & time=='2020-01-03 15:00:00'").disp.values[0] == pytest.approx(149.05928)
    assert srmc.srmc.min() == pytest.approx(460.13092)
    assert gen_cap_op.query('tech==18 & zone==16').cap_op.values[0] == pytest.approx(2280)
    assert cdu.loc[2022, 16, 18].cap_op == pytest.approx(2280)
