from common.yaml_scrapping import YamlService

class PerformanceMetrics:
    @staticmethod
    def get_performance_metrics() -> list[dict]:
        data = YamlService.getYamlData()
        metrics = data['performance_metrics']
        return list(map(lambda x : x['name'], metrics))

    @staticmethod
    def get_performance_metric_details(metricId:str) -> dict:
        data = YamlService.getYamlData()
        metrics = data['performance_metrics']

        metric = list(filter(lambda x : x['name'] == metricId, metrics))
        if len(metric) != 1:
            raise ValueError("The performance metric was not found or has at least two models with the same name/id")

        return metric[0]
        