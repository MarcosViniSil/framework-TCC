import json

import pytest
import yaml

from validator import validate_yaml as validator


@pytest.fixture(autouse=True)
def _no_hf_network(monkeypatch):
    """Avoid network calls to Hugging Face; models are considered valid by default."""
    monkeypatch.setattr(validator, "_hf_model_exists", lambda model_id: True)


def _write_config(tmp_path, *, models=None, quality_metrics=None,
                  performance_metrics=None, dataset_path=None):
    config = {
        "dataset": {
            "path": str(dataset_path) if dataset_path else str(tmp_path / "corpus.jsonl"),
            "source_lang": "en",
            "target_lang": "pt",
        },
        "models": models if models is not None else [{"id": "m1", "name": "Helsinki-NLP/opus-mt-tc-big-en-pt"}],
        "quality_metrics": quality_metrics if quality_metrics is not None else [{"name": "bleu"}],
        "performance_metrics": (
            performance_metrics if performance_metrics is not None else [{"name": "inference_time"}]
        ),
    }
    path = tmp_path / "config.yaml"
    path.write_text(yaml.safe_dump(config), encoding="utf-8")
    return path


def _write_corpus_jsonl(tmp_path, records):
    corpus = tmp_path / "corpus.jsonl"
    corpus.write_text(
        "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in records),
        encoding="utf-8",
    )
    return corpus


def test_no_models_raise(tmp_path):
    cfg = _write_config(tmp_path, models=[])
    with pytest.raises(ValueError, match="no model"):
        validator.validate_yaml_file(str(cfg))


def test_unsupported_quality_metric_raise(tmp_path):
    _write_corpus_jsonl(tmp_path, [{"en": "hi", "pt": "oi"}])
    cfg = _write_config(tmp_path, quality_metrics=[{"name": "meteor"}])
    with pytest.raises(ValueError, match="meteor"):
        validator.validate_yaml_file(str(cfg))


def test_unsupported_performance_metric_raise(tmp_path):
    _write_corpus_jsonl(tmp_path, [{"en": "hi", "pt": "oi"}])
    cfg = _write_config(tmp_path, performance_metrics=[{"name": "latency"}])
    with pytest.raises(ValueError, match="latency"):
        validator.validate_yaml_file(str(cfg))


def test_model_not_found_on_huggingface_raise(tmp_path, monkeypatch):
    _write_corpus_jsonl(tmp_path, [{"en": "hi", "pt": "oi"}])
    monkeypatch.setattr(validator, "_hf_model_exists", lambda model_id: False)
    cfg = _write_config(tmp_path)
    with pytest.raises(ValueError, match="not found on HuggingFace"):
        validator.validate_yaml_file(str(cfg))


def test_valid_config_passes(tmp_path):
    _write_corpus_jsonl(tmp_path, [{"en": "hi", "pt": "oi"}, {"en": "bye", "pt": "tchau"}])
    cfg = _write_config(tmp_path)
    validator.validate_yaml_file(str(cfg))  


def test_missing_corpus_raise(tmp_path):
    cfg = _write_config(tmp_path, dataset_path=tmp_path / "missing.jsonl")
    with pytest.raises(FileNotFoundError, match="missing"):
        validator.validate_yaml_file(str(cfg))


def test_json_array_converted_to_jsonl(tmp_path):
    json_corpus = tmp_path / "corpus.json"
    json_corpus.write_text(
        json.dumps([{"en": "hi", "pt": "oi"}, {"en": "bye", "pt": "tchau"}], ensure_ascii=False),
        encoding="utf-8",
    )
    cfg = _write_config(tmp_path, dataset_path=json_corpus)
    validator.validate_yaml_file(str(cfg))

    jsonl_path = tmp_path / "corpus.jsonl"
    assert jsonl_path.exists()
    lines = jsonl_path.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 2
    assert all(json.loads(line) for line in lines)


def test_jsonl_with_invalid_line_raise(tmp_path):
    corpus = tmp_path / "corpus.jsonl"
    corpus.write_text('{"en": "hi", "pt": "oi"}\ninvalid line\n', encoding="utf-8")
    cfg = _write_config(tmp_path, dataset_path=corpus)
    with pytest.raises(ValueError, match="line 2"):
        validator.validate_yaml_file(str(cfg))
