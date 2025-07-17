import yaml

config = None
with open('gm_ai.config.yaml', 'r') as file:
    config = yaml.safe_load(file.read())
