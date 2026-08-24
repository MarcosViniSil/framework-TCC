from common.executions import Executions
from common.models import Models
from common.performance_metrics import PerformanceMetrics
from common.quality_metrics import QualityMetrics
from common.reporting import Reporting
from dataset.load_dataset import convert_corpus_to_dict
from models.modelManager import ModelManager
from validator.validate_yaml import validate_yaml_file


YAML_PATH = "../model.yaml"

#validate_yaml_file(YAML_PATH)
#convert_corpus_to_dict(YAML_PATH)

modelManager = ModelManager()
models = Models.get_models_ids()
translation = modelManager.translate("hello, world!",models[2])
print(translation)