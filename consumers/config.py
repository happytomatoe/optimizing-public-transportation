import yaml


def load_config():
    return yaml.safe_load(open("../config.yml"))


def get_topic_prefix():
    config = load_config()
    return config['kafka']['topics']['prefix']
