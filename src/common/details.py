from common.yaml_scrapping import YamlService


class ProjectDetails:
    @staticmethod
    def get_project_name() -> list[dict]:
        data = YamlService.getYamlData()
        experiment = data["experiment"]

        return experiment["name"]

    @staticmethod
    def get_project_description() -> dict:
        data = YamlService.getYamlData()
        experiment = data["experiment"]

        return experiment["description"]

    @staticmethod
    def get_project_default_result_folder() -> dict:
        data = YamlService.getYamlData()
        experiment = data["experiment"]

        return experiment["output_dir"]
