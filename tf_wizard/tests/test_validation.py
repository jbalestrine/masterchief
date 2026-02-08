import pytest
from tf_wizard.schema import ModuleSpec


def test_valid_spec():
    s = {
        "module_name": "x",
        "provider": "aws",
        "variables": [{"name":"region"}],
    }
    m = ModuleSpec(**s)
    assert m.module_name == 'x'


def test_invalid_provider():
    s = {"module_name":"x","provider":"digitalocean"}
    with pytest.raises(Exception):
        ModuleSpec(**s)
