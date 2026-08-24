from common.yaml_scrapping import YamlService

class QualityMetrics:
    @staticmethod
    def get_quality_metrics_library() -> list[dict]:
        data = YamlService.getYamlData()
        metrics = data['quality_metrics']
        return list(map(lambda x : x['library'], metrics))

    @staticmethod
    def get_quality_metrics_details(qualityId:str) -> dict:
        data = YamlService.getYamlData()
        metrics = data['quality_metrics']

        metric = list(filter(lambda x : x['library'] == qualityId, metrics))
        if len(metric) != 1:
            raise ValueError("The quality metric was not found or has at least two models with the same name/id")

        return metric[0]
        