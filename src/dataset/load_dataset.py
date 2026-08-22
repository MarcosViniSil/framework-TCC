from pathlib import Path

import yaml
import json
import logging

logger = logging.getLogger(__name__)

def _get_corpus_path(yaml_path) -> str:
    with open(yaml_path, 'r', encoding='utf-8') as file:
        data = yaml.safe_load(file)

        return data['dataset']['path']

def convert_corpus_to_dict(yaml_path) -> dict:
    corpus_path = _get_corpus_path(yaml_path)

    with open(corpus_path, 'r', encoding='utf-8') as json_data:
        try:
            if corpus_path.endswith(".json"):
                dados = json.load(json_data)
            else:
                dados = [json.loads(linha) for linha in json_data if linha.strip()] 
            print(dados)
        except Exception as e:
            logger.warning(
                "the following error occurred when trying to convert json to dict: {}", str(e)
            )
            raise ValueError("An error occurred when trying to convert json to dict")


convert_corpus_to_dict("./model.yaml")


