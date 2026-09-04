from common.yaml_scrapping import YamlService


class Models:
    @staticmethod
    def get_models_ids() -> list[dict]:
        data = YamlService.getYamlData()
        models_list = data["models"]
        return list(map(lambda x: x["name"], models_list))

    @staticmethod
    def get_models() -> list[dict]:
        data = YamlService.getYamlData()
        return data["models"]

    @staticmethod
    def get_model_details(modelId: str) -> dict:
        data = YamlService.getYamlData()
        models_list = data["models"]

        model = list(filter(lambda x: x["name"] == modelId, models_list))
        if len(model) != 1:
            raise ValueError(
                "The model was not found or has at least two models with"
                "the same name/id"
            )

        return model[0]
