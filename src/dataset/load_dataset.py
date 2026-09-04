import sys
from pathlib import Path

import yaml
import json
import logging

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from domain.dataset import DataSet

logger = logging.getLogger(__name__)


def _get_project_root():
    current_file = Path(__file__).resolve()
    project_root = current_file.parent.parent.parent
    return project_root


def _get_corpus_path(yaml_path) -> str:
    with open(yaml_path, "r", encoding="utf-8") as file:
        data = yaml.safe_load(file)

        return data["dataset"]["path"]


def convert_corpus_to_dict(yaml_path) -> DataSet:
    corpus_path = _get_corpus_path(yaml_path)
    project_root = _get_project_root()
    absolute_path = project_root / corpus_path.lstrip(". /")

    with open(absolute_path, "r", encoding="utf-8") as json_data:
        try:
            if corpus_path.endswith(".json"):
                corpus = json.load(json_data)
            else:
                corpus = [json.loads(line) for line in json_data if line.strip()]
            return DataSet(corpus if corpus else [{}])

        except Exception as e:
            logger.warning(
                "the following error occurred when trying to convert json to dict: {}",
                str(e),
            )
            raise ValueError("An error occurred when trying to convert json to dict")
