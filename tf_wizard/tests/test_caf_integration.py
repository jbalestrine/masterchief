import json
from tf_wizard.generator import generate_files


def test_generate_azurerm_with_caf_options():
    spec = {
        "module_name": "caf_example",
        "provider": "azurerm",
        "variables": [
            {"name": "location", "type": "string", "default": "eastus"}
        ],
        "resources": [],
        "outputs": [],
        "caf": {
            "naming_convention": "caf",
            "landing_zone": "foundation",
            "network_topology": "hub-spoke",
            "identity": "user",
            "enable_monitoring": True,
            "enable_policy": True
        }
    }

    files = generate_files(spec)
    assert "main.tf" in files
    main = files["main.tf"]
    # expect resource group and hub vnet when hub-spoke selected
    assert "azurerm_resource_group" in main
    assert "azurerm_virtual_network" in main or "azurerm_subnet" in main
    # README should include CAF metadata
    assert "CAF options" in files.get("README.md", "")
