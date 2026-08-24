from common.yaml_scrapping import YamlService

class Reporting:
    @staticmethod
    def get_reporting() -> list[dict]:
        data = YamlService.getYamlData()
        return data['reporting']['plots']
        