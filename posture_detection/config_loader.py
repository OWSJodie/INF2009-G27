import os
import json

def load_config(config_path=None):
    if config_path is None:
        config_path = os.path.join(os.path.dirname(__file__), "config.json")
    
    with open(config_path, 'r') as f:
        config = json.load(f)
    return config
