# CEMO tests for basic instantiation
import pytest
import os.path


def test_database():
    assert os.path.isfile('cemo_db/cemo.db'), "Database not found!"


def test_model_creation(model, benchmark):
    assert model.name == benchmark.name
    assert model.is_constructed() is False


@pytest.mark.skipif(not os.path.isfile('cemo_db/cemo.db'),
                    reason="Database required")
def test_model_instantiation(instance, benchmark):
    assert instance.name == benchmark.name, "Instance name does not match"
    assert instance.is_constructed() is True
    assert instance.Z.data() == benchmark.Z.data(), "Mismatch in test regions"
    assert instance.N.data() \
        == benchmark.N.data(), "Mismatch in list of gen techs"
    assert instance.Inv.data() \
        == benchmark.Inv.data(), "Mismatch of investment periods"
