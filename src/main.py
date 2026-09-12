from common.logging_config import configure_logging

configure_logging()

from pipeline.pipeline import run
from validator.validate_yaml import validate_yaml_file

YAML_PATH = "../model.yaml"
validate_yaml_file(YAML_PATH)

run()
