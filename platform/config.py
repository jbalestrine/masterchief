"""
Configuration management for MasterChief platform
"""

import yaml
from pathlib import Path
from typing import Dict, Any

DEFAULT_CONFIG_PATHS = [
    '/etc/masterchief/config.yml',
    Path.home() / '.masterchief' / 'config.yml',
    Path(__file__).parent.parent / 'config.yml',
]

DEFAULT_CONFIG = {
    'platform': {
        'version': '1.0.0',
        'install_dir': '/opt/masterchief',
        'config_dir': '/etc/masterchief',
        'log_dir': '/var/log/masterchief',
        'data_dir': '/var/lib/masterchief',
    },
    'api': {
        'host': '0.0.0.0',
        'port': 8443,
        'ssl': True,
    },
    'database': {
        'type': 'postgresql',
        'host': 'localhost',
        'port': 5432,
        'database': 'masterchief',
        'user': 'masterchief',
        'password': '',
    },
    'monitoring': {
        'enabled': True,
        'prometheus_port': 9090,
        'grafana_port': 3000,
    },
    'security': {
        'cis_compliance': True,
        'firewall_enabled': True,
        'auto_updates': True,
    },
}

def load_config() -> Dict[str, Any]:
    """Load configuration from file or use defaults"""
    
    # Try to load from config files
    for config_path in DEFAULT_CONFIG_PATHS:
        if Path(config_path).exists():
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
                # Merge with defaults
                return deep_merge(DEFAULT_CONFIG, config)
    
    # Use defaults if no config file found
    return DEFAULT_CONFIG.copy()

def deep_merge(base: Dict, update: Dict) -> Dict:
    """Deep merge two dictionaries"""
    result = base.copy()
    for key, value in update.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    return result

def save_config(config: Dict[str, Any], path: str = None):
    """Save configuration to file"""
    if path is None:
        path = DEFAULT_CONFIG_PATHS[0]
    
    config_path = Path(path)
    config_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(config_path, 'w') as f:
        yaml.dump(config, f, default_flow_style=False)
