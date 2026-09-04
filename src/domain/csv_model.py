from dataclasses import dataclass
from datetime import datetime


@dataclass
class CSVModel:
    sample_id: int
    timestamp: datetime
    source_lang: str
    target_lang: str
    original_sentence: str
    original_translation: str
    generated_translation: str
    model_name: str

    # Metrics
    BERTscore: float
    BLEU: float
    chrf: float

    # CPU
    cpu_average_usage: float
    cpu_samples: int
    cpu_max_usage: float
    cpu_min_usage: float

    # Memory
    additional_memory: float
    initial_memory: float
    final_memory: float
    peak_memory: float

    # Inference
    inference_time: float
