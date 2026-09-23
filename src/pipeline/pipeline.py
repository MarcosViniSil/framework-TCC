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

from tqdm import tqdm

from pipeline.cache import append_to_cache, get_value_cached, key_exists_on_cache
from pipeline.generate_report import generate_excel
from ws.jobs import send_message

YAML_PATH = "../model.yaml"


def define_header() -> list[str]:
    return [
        "sample_id",
        "timestamp",
        "source_lang",
        "target_lang",
        "original_sentence",
        "original_translation",
        "generated_translation",
        "model_name",
        "BLEU",
        "BERTscore",
        "chrf",
        # CPU
        "cpu_average_usage",
        "cpu_samples",
        "cpu_max_usage",
        "cpu_min_usage",
        # Memory
        "additional_memory",
        "initial_memory",
        "final_memory",
        "peak_memory",
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
        "sample_id": data["id"],
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
        "additional_memory": efficiency_metrics.memory_efficiency.additional_memory,
        "initial_memory": efficiency_metrics.memory_efficiency.initial_memory,
        "final_memory": efficiency_metrics.memory_efficiency.final_memory,
        "peak_memory": efficiency_metrics.memory_efficiency.memory_peak,
        # Inference
        "inference_time": efficiency_metrics.inference.inferenceTime,
    }

    return CSVModel(**row)


async def run():
    print("comecou")
    efficiency = Efficiency()
    metrics = Metrics()

    modelManager = ModelManager()
    models_id = Models.get_models_ids()

    dataset: DataSet = convert_corpus_to_dict(YAML_PATH)

    data_to_csv = []
    header = None

    total_translations = len(dataset.corpus) * len(models_id)

    count_translation_model = {}

    for model_id in models_id:
        count_translation_model[model_id] = 0

    completed = 0
    with tqdm(total=total_translations, desc="Translating", unit="translation") as progress:
        for i, corpus in enumerate(dataset.corpus):
            for j, model_id in enumerate(models_id):
                try:
                    progress.set_postfix(model=model_id, sample=corpus['id'])


                    if i == j == 0:
                        header = define_header()

                    key = (corpus['id'], model_id)

                    if key_exists_on_cache(key):
                        data_to_csv.append(get_value_cached(key))
                        progress.update(1)

                        completed += 1
                        count_translation_model[model_id] += 1

                        await send_message({
                            "type": "progress",
                            "sample": corpus["en"],
                            "model": model_id,
                            "completed": completed,
                            "total": total_translations,
                            "models_count": count_translation_model
                        })


                        continue


                    efficiency.start_collection()

                    translation: TranslationResult = modelManager.translate(
                        corpus[dataset.source_langue], model_id
                    )

                    bleu_metric: MetricResult = metrics.bleu(
                        corpus[dataset.target_language], translation.target_text
                    )
                    bertScore: MetricResult = metrics.BERTscore(
                        corpus[dataset.target_language], translation.target_text
                    )
                    chrf_metric: MetricResult = metrics.chrf(
                        corpus[dataset.target_language], translation.target_text
                    )

                    efficiency.stop_collection()
                    efficiency_metrics: EfficiencyModel = efficiency.collect_metrics()

                    efficiency.clear()

                    csvModel = createCSV_model(
                        data=corpus,
                        metrics=[bleu_metric, bertScore, chrf_metric],
                        translation=translation,
                        efficiency_metrics=efficiency_metrics,
                        model_name=model_id,
                    )

                    data_to_csv.append(csvModel)
                    append_to_cache(key,csvModel)

                    progress.update(1)

                    count_translation_model[model_id] += 1
                    completed += 1

                    await send_message({
                        "type": "progress",
                        "sample": corpus["en"],
                        "model": model_id,
                        "completed": completed,
                        "total": total_translations,
                        "models_count": count_translation_model
                        
                    })
                except Exception as e:
                    await send_message({
                        "type": "error",
                        "message": str(e),
                        "timestamp": str(datetime.now())
                    })
                    return
                

    if header is not None:
        generate_excel(header, data_to_csv)
    else:
        raise ValueError("it was not possible to generate csv. Reason: header is None")

if __name__ == "__main__":
    import asyncio

    asyncio.run(run())
