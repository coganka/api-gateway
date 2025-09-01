import yaml
import os


def load_config(path="gateway_config.yaml"):
    base_dir = os.path.dirname(os.path.dirname(__file__))
    full_path = os.path.join(base_dir, path)

    with open(full_path, "r") as f:
        return yaml.safe_load(f)