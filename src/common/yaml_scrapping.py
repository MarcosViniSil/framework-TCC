import yaml

YAML_PATH = "../model.yaml"


class YamlService:
    @staticmethod
    def getYamlData() -> list[dict]:
        with open(YAML_PATH, "r", encoding="utf-8") as file:
            data = yaml.safe_load(file)
            return data
