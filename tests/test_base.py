# openCEM tests for basic instantiation


def test_model_creation(model, benchmark):
    assert model.name == benchmark.name, "Test model name does not match saved data"
    assert model.is_constructed() is False


def test_model_instantiation(instance, benchmark):
    assert instance.name == benchmark.name, "Instance name does not match"
    assert instance.is_constructed() is True
    assert instance.zones.data() == benchmark.zones.data(), "Mismatch in test regions"
    assert instance.all_tech.data() \
        == benchmark.all_tech.data(), "Mismatch in list of gen techs"
