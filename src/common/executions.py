from common.yaml_scrapping import YamlService

class Executions:
    @staticmethod
    def get_execution() -> list[dict]:
        data = YamlService.getYamlData()
        return data['executions']
            