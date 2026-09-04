from common.models import Models
from dataset.load_dataset import convert_corpus_to_dict
from domain.csv_model import CSVModel
from domain.dataset import DataSet
from domain.efficiency import EfficiencyModel
from domain.metrics import MetricResult
from domain.translationResult import TranslationResult
from efficiency.efficiency import Efficiency
from metrics.metrics import Metrics
from models.modelManager import ModelManager
from datetime import datetime

from pipeline.generate_csv import generate_csv

YAML_PATH = "../model.yaml"


def define_header(metrics: list[MetricResult]) -> list[str]:
    return [
        "id",
        "timestamp",
        "source_lang",
        "target_lang",
        "original_sentence",
        "original_translation",
        "generated_translation",
        "model_name",
        *[metric.metric_name for metric in metrics],
        # CPU
        "cpu_average_usage",
        "cpu_samples",
        "cpu_max_usage",
        "cpu_min_usage",
        # Memory
        "memory_additional",
        "memory_initial",
        "memory_final",
        "memory_peak",
        # Inference
        "inference_time",
    ]


def createCSV_model(
    data,
    metrics: list[MetricResult],
    translation: TranslationResult,
    efficiency_metrics: EfficiencyModel,
    model_name: str,
) -> CSVModel:

    row = {
        "id": data["id"],
        "timestamp": datetime.now(),
        "source_lang": translation.source_lang,
        "target_lang": translation.target_lang,
        "original_sentence": translation.source_text,
        "original_translation": data["pt"],
        "generated_translation": translation.target_text,
        "model_name": model_name,
        # Metrics
        **{metric.metric_name: metric.value for metric in metrics},
        # CPU
        "cpu_average_usage": efficiency_metrics.cpy_efficiency.average_usage,
        "cpu_samples": efficiency_metrics.cpy_efficiency.samples,
        "cpu_max_usage": efficiency_metrics.cpy_efficiency.max_usage,
        "cpu_min_usage": efficiency_metrics.cpy_efficiency.min_usage,
        # Memory
        "memory_additional": efficiency_metrics.memory_efficiency.additional_memory,
        "memory_initial": efficiency_metrics.memory_efficiency.initial_memory,
        "memory_final": efficiency_metrics.memory_efficiency.final_memory,
        "memory_peak": efficiency_metrics.memory_efficiency.memory_peak,
        # Inference
        "inference_time": efficiency_metrics.inference.inferenceTime,
    }

    return CSVModel(**row)


def run():
    efficiency = Efficiency()
    metrics = Metrics()

    modelManager = ModelManager()
    models_id = Models.get_models_ids()

    dataset: DataSet = convert_corpus_to_dict(YAML_PATH)

    data_to_csv = []
    header = None

    for i, data in enumerate(dataset.corpus):
        for j, model_id in enumerate(models_id):
            efficiency.start_collection()

            translation: TranslationResult = modelManager.translate(
                data["en"], model_id
            )

            bleu_metric: MetricResult = metrics.bleu(
                data["pt"], translation.target_text
            )
            bertScore: MetricResult = metrics.BERTscore(
                data["pt"], translation.target_text
            )
            chrf_metric: MetricResult = metrics.chrf(
                data["pt"], translation.target_text
            )

            efficiency.stop_collection()
            efficiency_metrics: EfficiencyModel = efficiency.collect_metrics()

            efficiency.clear()

            csvModel = createCSV_model(
                data=data,
                metrics=[bleu_metric, bertScore, chrf_metric],
                translation=translation,
                efficiency_metrics=efficiency_metrics,
                model_name=model_id,
            )

            if i == j == 0:
                header = define_header(metrics=[bleu_metric, bertScore, chrf_metric])

            data_to_csv.append(csvModel)

    if header is not None:
        generate_csv(header, data_to_csv)
    else:
        raise ValueError("it was not possible to generate csv. Reason: header is None")
