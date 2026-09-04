from dataclasses import dataclass


@dataclass
class DataSet:
    corpus: list[dict]
    source_langue: str
    target_language: str
