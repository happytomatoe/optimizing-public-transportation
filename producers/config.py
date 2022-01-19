import yaml


def load_config():
    return yaml.safe_load(open("config.yml"))
