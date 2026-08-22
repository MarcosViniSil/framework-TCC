"""Validation of the experiment configuration YAML file."""

from __future__ import annotations

import json
import logging
from pathlib import Path

import yaml

logger = logging.getLogger(__name__)

SUPPORTED_QUALITY_METRICS = {"bleu", "chrf", "bertscore", "comet"}
SUPPORTED_PERFORMANCE_METRICS = {
    "inference_time",
    "memory_usage",
    "cpu_usage",
    "gpu_utilization",
}

HF_MODEL_API = "https://huggingface.co/api/models/{}"


def _hf_model_exists_api(model_id: str) -> bool:
    """Fallback: query the HuggingFace API with urllib (no dependencies)."""
    import urllib.error
    import urllib.request

    req = urllib.request.Request(
        HF_MODEL_API.format(model_id), headers={"User-Agent": "mtbench-validator"}
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status == 200
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            return False
        logger.warning(
            "Could not verify model '%s' on HuggingFace (HTTP %s); skipping.",
            model_id,
            exc.code,
        )
        return True
    except Exception as exc: 
        logger.warning(
            "Could not verify model '%s' on HuggingFace (%s); skipping.",
            model_id,
            exc,
        )
        return True


def _hf_model_exists(model_id: str) -> bool:
    """Return True if the model exists on the HuggingFace Hub."""
    try:
        from huggingface_hub import model_info
    except ImportError:
        return _hf_model_exists_api(model_id)
    try:
        model_info(model_id)
        return True
    except Exception as exc:  # noqa: BLE001
        status = getattr(getattr(exc, "response", None), "status_code", None)
        if status == 404:
            return False
        logger.warning(
            "Could not verify model '%s' on HuggingFace (%s); skipping.",
            model_id,
            exc,
        )
        return True


def _validate_hf_models(raw) -> None:
    models = raw.get("models") or []
    for model in models:
        model_id = model.get("name") if isinstance(model, dict) else None
        if not model_id:
            raise ValueError(f"Model without HuggingFace id ('name'): {model}")
        if not _hf_model_exists(model_id):
            raise ValueError(f"Model not found on HuggingFace: {model_id}")


def _json_to_jsonl(corpus: Path) -> Path:
    """Convert json to jsonl and return the jsonl path."""
    with corpus.open(encoding="utf-8") as json_file:
        dados = json.load(json_file)

    jsonl_path = corpus.with_suffix(".jsonl")
    with jsonl_path.open("w", encoding="utf-8") as jsonl_file:
        for register in dados:
            jsonl_file.write(json.dumps(register, ensure_ascii=False) + "\n")
    return jsonl_path

def _validate_models(raw) -> None:
    models = raw.get("models") or []
    if not isinstance(models, list) or not models:
        raise ValueError("There is no model defined. Please, specify which models you'd like to use.")

def _validate_metrics(raw) -> None:
    quality_metrics = raw.get("quality_metrics") or []
    if not isinstance(quality_metrics, list) or not quality_metrics:
        raise ValueError("There are no quality metrics defined. Please specify at least one quality metric.")
    unsupported = [
        m.get("name") for m in quality_metrics if m.get("name") not in SUPPORTED_QUALITY_METRICS
    ]
    if unsupported:
        raise ValueError(
            f"Unsupported quality metrics: {unsupported}. "
            f"Supported: {sorted(SUPPORTED_QUALITY_METRICS)}"
        )


def _validate_performance_metrics(raw) -> None:
    performance_metrics = raw.get("performance_metrics") or []
    if not isinstance(performance_metrics, list):
        raise ValueError("'performance_metrics' must be a list.")
    unsupported = [
        m.get("name")
        for m in performance_metrics
        if m.get("name") not in SUPPORTED_PERFORMANCE_METRICS
    ]
    if unsupported:
        raise ValueError(
            f"Unsupported performance metrics: {unsupported}. "
            f"Supported: {sorted(SUPPORTED_PERFORMANCE_METRICS)}"
        )

def _validate_dataset_existence(corpus_path,path) -> Path:
    corpus = Path(corpus_path)
    if not corpus.is_absolute():
        corpus = (path.parent / corpus).resolve()
    if not corpus.exists():
        raise FileNotFoundError(f"Corpus not found: {corpus}")

    return corpus

def _validate_dataset(raw) -> Path:
    dataset = raw.get("dataset") or {}
    ds_path = dataset.get("path")
    if not ds_path:
        raise ValueError("Corpus not found")

    return ds_path

def _is_json_file(corpus) -> bool:
    text = corpus.read_text(encoding="utf-8")
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        data = None

    return data

def _convert_and_validate_jsonl_structure(data,corpus) -> None:
    text = corpus.read_text(encoding="utf-8")
    if data is not None:
        if isinstance(data, list):
            jsonl_path = _json_to_jsonl(corpus)
            logger.info("Corpus JSON converted to JSONL: %s", jsonl_path)
            return
        if len([line for line in text.splitlines() if line.strip()]) == 1:
            return
        raise ValueError(f"Corpus JSON is not an array: {corpus}")
    
def _validate_dataset_lines(corpus) -> None:
    text = corpus.read_text(encoding="utf-8")
    for i, line in enumerate(text.splitlines(), start=1):
        if not line.strip():
            continue
        try:
            json.loads(line)
        except json.JSONDecodeError:
            raise ValueError(f"Invalid corpus at line {i} (not json neither jsonl):")    


def validate_yaml_file(yaml_path: str) -> None:
    path = Path(yaml_path)
    with path.open(encoding="utf-8") as f:
        raw = yaml.safe_load(f)

    _validate_models(raw)

    _validate_metrics(raw)

    _validate_performance_metrics(raw)

    ds_path = _validate_dataset(raw)

    corpus = _validate_dataset_existence(ds_path,path)

    data = _is_json_file(corpus)
    if data is not None:
        _convert_and_validate_jsonl_structure(data,corpus)

    _validate_dataset_lines(corpus)

    _validate_hf_models(raw)


if __name__ == "__main__":
    validate_yaml_file("../../model.yaml")