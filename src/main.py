from common.executions import Executions
from common.models import Models
from common.performance_metrics import PerformanceMetrics
from common.quality_metrics import QualityMetrics
from common.reporting import Reporting
from dataset.load_dataset import convert_corpus_to_dict
from validator.validate_yaml import validate_yaml_file


YAML_PATH = "../model.yaml"

validate_yaml_file(YAML_PATH)
#convert_corpus_to_dict(YAML_PATH)

print(Models.get_models())
print(Models.get_model_details("facebook/nllb-200-distilled-600M"))
print(QualityMetrics.get_quality_metrics_library())
print(QualityMetrics.get_quality_metrics_details("bert_score"))
print(PerformanceMetrics.get_performance_metrics())
print(PerformanceMetrics.get_performance_metric_details("cpu_usage"))
print(Executions.get_execution())
print(Reporting.get_reporting())