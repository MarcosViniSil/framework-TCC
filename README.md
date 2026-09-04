# MT Evaluation Framework

A YAML-driven framework for evaluating machine translation (MT) models on
**English → Portuguese (en→pt)**. Given a sentence-level parallel corpus and a
list of Hugging Face Seq2Seq models, it translates every sentence with every
model, computes automatic **quality metrics** (BLEU, chrF, BERTScore) and
collects **performance metrics** (CPU usage, memory usage, inference time), and
finally exports everything to a styled **Excel report**.

Built as part of an undergraduate thesis (TCC) on the evaluation of neural MT
models for the en→pt language pair.

---

## Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Project structure](#project-structure)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
- [Configuration (`model.yaml`)](#configuration-modelyaml)
- [Dataset format](#dataset-format)
- [How the pipeline works](#how-the-pipeline-works)
- [Quality metrics](#quality-metrics)
- [Performance metrics](#performance-metrics)
- [Caching](#caching)
- [Output — Excel report](#output--excel-report)
- [Supported models](#supported-models)
- [Adding a new model](#adding-a-new-model)
- [Running tests](#running-tests)
- [Known limitations](#known-limitations)

---

## Features

- **Zero-code experiment changes** — swap models, metrics, dataset or languages
  by editing a single `model.yaml` file.
- **Multiple architectures out of the box** — Opus-MT, NLLB-200 and M2M-100,
  all loaded lazily and reused across samples (no reload per sentence).
- **Quality metrics** — BLEU (NLTK), chrF (SacreBLEU) and BERTScore
  (target language `pt`).
- **Performance metrics** — CPU usage sampling (background thread, `psutil`),
  process memory sampling (RSS) with peak tracking, and per-sentence inference
  time (`time.perf_counter`).
- **SQLite cache** — one row per `(sample_id, model)`. Interrupted or repeated
  runs skip already-translated samples instead of re-running expensive
  inference.
- **Config validation before execution** — checks that models exist on the
  Hugging Face Hub, metrics are supported, the corpus file exists and is valid
  JSON/JSONL (auto-converts a JSON array to JSONL).
- **Styled Excel export** — formatted header, title, auto-filter, frozen panes,
  alternating rows and auto-sized columns.

---

## Architecture

The framework is organized as a small set of layered packages under `src/`:

```
model.yaml ──▶ validator ──▶ pipeline ──▶ generate_report ──▶ results/*.xlsx
                                 │
              ┌──────────────────┼───────────────────┐
              ▼                  ▼                   ▼
        dataset loader     ModelManager        Efficiency / Metrics
              │               │  │                 (collectors)
        corpus (JSONL)    ModelFactory        + SQLite cache
                             │
                 OpusMT · NLLB · M2M100
```

Flow at a glance:

1. `src/main.py` validates `model.yaml` (see `validator/`) and starts the
   pipeline.
2. `pipeline.py` loads the corpus into a `DataSet` and iterates over every
   `(sample, model)` pair.
3. If the pair is already cached, the stored row is reused and the model is
   **not** invoked again.
4. Otherwise the efficiency collectors are started, the model translates the
   source sentence, the three quality metrics are computed against the
   reference translation, and the collectors are stopped.
5. Results are assembled into a `CSVModel` row (see `domain/`), persisted to
   the SQLite cache and appended to the in-memory list.
6. At the end, `generate_excel.py` writes a formatted `.xlsx` file to the
   `experiment.output_dir` folder (default `./results`).

> **Path conventions.** The code locates `model.yaml` relative to the current
> working directory (`../model.yaml`), and report/cache paths are also resolved
> from the CWD. Because of this, the application is designed to run from inside
> the `src/` directory — see [Usage](#usage).

---

## Project structure

```
framework_TCC/
├── model.yaml                 # Experiment configuration (single source of truth)
├── gnome.jsonl                # Sample parallel corpus (en/pt) used by default
├── requirements.txt           # Python dependencies
├── test.py                    # Standalone smoke script
├── tests/
│   ├── conftest.py            # Adds src/ to sys.path for pytest
│   └── test_validate_yaml.py  # Unit tests for the YAML validator
└── src/
    ├── main.py                # Entry point: validate config, then run
    ├── pipeline/
    │   ├── pipeline.py        # Orchestrates the evaluation loop
    │   ├── cache.py           # SQLite cache helpers (cache/cache.db)
    │   └── generate_report.py # Excel report generation (openpyxl)
    ├── validator/
    │   └── validate_yaml.py   # Pre-flight configuration validation
    ├── dataset/
    │   └── load_dataset.py    # JSON/JSONL corpus → DataSet
    ├── models/
    │   ├── translationModel.py    # Abstract base model (ABC)
    │   ├── modelManager.py        # Lazy loading + reuse of loaded models
    │   ├── factory/modelFactory.py# HF id → concrete model class
    │   └── impl/
    │       ├── opusMT.py          # Helsinki-NLP Opus-MT
    │       ├── NLLB.py            # Facebook NLLB-200
    │       └── M2M100.py          # Facebook M2M-100
    ├── metrics/
    │   └── metrics.py         # BLEU / chrF / BERTScore implementations
    ├── efficiency/
    │   └── efficiency.py      # CPU / memory / inference-time collectors
    ├── domain/                # Dataclasses (rows and result objects)
    │   ├── dataset.py, csv_model.py, translationResult.py
    │   ├── metrics.py, efficiency.py
    │   ├── cpu_efficiency.py, memory_efficiency.py, inference.py
    ├── common/                # YAML accessors grouped by config section
    │   ├── yaml_scrapping.py, models.py, details.py
    │   ├── quality_metrics.py, performance_metrics.py
    │   ├── executions.py, reporting.py
    ├── results/               # Generated Excel reports (git-ignored)
    └── cache/                 # SQLite cache.db (git-ignored)
```

---

## Requirements

- **Python 3.10+**
- Dependencies in `requirements.txt`:

| Package         | Minimum version | Purpose                                  |
| --------------- | --------------- | ---------------------------------------- |
| `pyyaml`        | 6.0             | Reading `model.yaml`                     |
| `torch`         | 2.1             | Model inference backend                  |
| `transformers`  | 4.40            | Hugging Face model loading / generation  |
| `sacrebleu`     | 2.4             | chrF computation                         |
| `sentencepiece` | 0.2.0           | Tokenizer support for NLLB / M2M-100     |
| `bert-score`    | 0.3.13          | BERTScore computation                    |
| `psutil`        | 5.9             | CPU / memory collection                  |

Two additional packages are imported at runtime but are **not** currently
listed in `requirements.txt`:

- `nltk` — used for sentence-level BLEU in `src/metrics/metrics.py`
- `openpyxl` — used for Excel export in `src/pipeline/generate_report.py`

Install them with:

```bash
pip install nltk openpyxl
```

A GPU is optional: models automatically fall back to CPU when CUDA is not
available, and fp16 is only applied when running on CUDA.

---

## Installation

```bash
# 1. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Extra runtime packages (see Requirements above)
pip install nltk openpyxl

# 4. Run the tests (optional)
pytest
```

> On the first run, each model is downloaded from the Hugging Face Hub, so an
> internet connection is required unless the models are already cached locally
> by `transformers`.

---

## Usage

Run from the `src/` directory (all internal paths — `model.yaml`,
`./results`, `cache/cache.db` — are resolved from the working directory):

```bash
cd src
python main.py
```

On startup, `validate_yaml_file("../model.yaml")` runs a pre-flight check:

1. at least one model is declared,
2. quality and performance metrics are among the supported sets,
3. the dataset file exists and is valid JSONL (a JSON array is automatically
   converted to JSONL),
4. every declared Hugging Face model id exists on the Hub (skipped gracefully
   on network errors; overridable in tests).

If validation passes, the evaluation runs. On completion, a formatted Excel
workbook named `<DD-MM-YYYY-HH-MM>_result.xlsx` (e.g.
`04-09-2026-00-17_result.xlsx`) is written to `src/results/`.

To force a fully fresh run (ignore cached translations), delete the cache
before running:

```bash
rm -f cache/cache.db
```

---

## Configuration (`model.yaml`)

All experiment settings live in a single YAML file at the repository root.
The current default configuration:

```yaml
experiment:
  name: "Comparison between translation models"
  description: "Evaluation of transformer models for English-Portuguese translation"
  output_dir: "./results"

dataset:
  path: "./gnome.jsonl"
  source_lang: "en"
  target_lang: "pt"
  format: "jsonl"

models:
  - id: "opus_mt-200M"
    name: "Helsinki-NLP/opus-mt-tc-big-en-pt"
  - id: "nllb-600M"
    name: "facebook/nllb-200-distilled-600M"
  - id: "m2m100-418M"
    name: "facebook/m2m100_418M"

quality_metrics:
  - name: "bleu"
  - name: "chrf"
  - name: "bertscore"

performance_metrics:
  - name: "inference_time"
  - name: "memory_usage"
  - name: "cpu_usage"

executions:
  quality_runs: 1
  seed: 42
  performance_runs: 3
  performance_strategy: "batch_sampling"
  seeds: [42, 123, 456]
```

### Section reference

| Section             | Field            | Meaning                                                           |
| ------------------- | ---------------- | ----------------------------------------------------------------- |
| `experiment.name`   | —                | Report title (written to the Excel header)                        |
| `experiment.description` | —          | Report subtitle                                                   |
| `experiment.output_dir` | —           | Folder (relative to CWD) where `.xlsx` reports are saved          |
| `dataset.path`      | —                | Corpus path, relative to the project root (JSON or JSONL)         |
| `dataset.source_lang` | —              | Key of the source field in each corpus record                     |
| `dataset.target_lang` | —              | Key of the reference translation field in each corpus record      |
| `models[]`          | `name`           | Hugging Face model id — this is what the factory maps to a class  |
| `models[]`          | `id`             | Local short label (stored on the model config; cache keys use `name`) |
| `quality_metrics[]` | `name`           | One of `bleu`, `chrf`, `bertscore` (validator also accepts `comet`) |
| `performance_metrics[]` | `name`       | One of `inference_time`, `memory_usage`, `cpu_usage` (validator also accepts `gpu_utilization`) |
| `executions`        | —                | Reserved for reproducibility settings (see [Known limitations](#known-limitations)) |

---

## Dataset format

The corpus is a **JSONL** file where each line is a JSON object containing an
`id`, the source sentence and the reference translation. The source/target
field names must match `dataset.source_lang` / `dataset.target_lang`:

```jsonl
{"id": 1, "en": "Accerciser", "pt": "Accerciser"}
{"id": 2, "en": "Give your application an accessibility workout", "pt": "Faça um exercício de acessibilidade em seu aplicativo"}
```

A plain **JSON array** file (`.json`) with the same record shape is also
accepted — the validator detects it during the pre-flight check and converts it
to JSONL automatically (writing a `.jsonl` sibling file).

The default `gnome.jsonl` contains GNOME UI strings (short, sentence-level
segments) in en→pt.

---

## How the pipeline works

`src/pipeline/pipeline.py::run()`:

1. Build the `Efficiency` (performance collectors) and `Metrics` instances and
   read the model list from the YAML.
2. Load the corpus into a `DataSet`.
3. For each `(sample, model)` pair:
   - If the cache already holds the pair, reuse the stored `CSVModel` row and
     move on (no translation, no metrics).
   - Otherwise:
     a. Start the enabled collectors (CPU thread, memory thread, inference
        timer) — `efficiency.start_collection()`.
     b. Translate the source sentence with the model.
     c. Compute BLEU, BERTScore and chrF against the reference translation.
     d. Stop the collectors and aggregate `CpuEfficiency`, `MemoryEfficiency`
        and `Inference` results.
     e. Build a `CSVModel` row, append it to the result list and persist it to
        the SQLite cache.
4. Export all rows to an Excel workbook.

Models are loaded once (lazily, on first use) and kept in memory by
`ModelManager`, so each model is downloaded/loaded only once per run.

---

## Quality metrics

Computed per sentence against the reference (`corpus[target_lang]`):

| Metric    | Library    | Notes                                          |
| --------- | ---------- | ---------------------------------------------- |
| **BLEU**  | NLTK       | Sentence-level BLEU with smoothing method 1; rounded to 3 decimals |
| **chrF**  | SacreBLEU  | `sentence_chrf`, rounded to 2 decimals         |
| **BERTScore** | `bert-score` | F1 for language `pt` (`lang="pt"`), rounded to 3 decimals |

The pipeline always computes the three metrics above for every sample,
regardless of the `quality_metrics` list (the list is validated, not yet used
to filter which metrics run — see [Known limitations](#known-limitations)).

---

## Performance metrics

Collected per sentence with background threads and a `psutil.Process` handle
bound to the current process:

| Metric           | Collection method                                                |
| ---------------- | ---------------------------------------------------------------- |
| **CPU usage**    | `process.cpu_percent(interval=0.05)` sampled in a thread; stores every sample; reports avg/max/min and sample count |
| **Memory usage** | RSS (`memory_info().rss`) sampled every ~10 ms; reports initial, final, peak and additional (peak − initial) memory in MB |
| **Inference time** | `time.perf_counter()` around the `translate()` call; formatted as `sec`/`min`/`h`/`days` |

Which collectors are started is driven by `performance_metrics` (the `Efficiency`
class reads the YAML to decide). Note that the aggregation step always reads
all three collectors, so the three default metrics (`cpu_usage`,
`memory_usage`, `inference_time`) are expected to be enabled together.

---

## Caching

`src/pipeline/cache.py` persists one row per translated sample in a SQLite
database at `cache/cache.db` (relative to the working directory):

- **Key**: the `(sample_id, model_name)` tuple.
- **Value**: the full `CSVModel` row serialized to JSON.
- **Behavior**: when a key already exists, the pipeline reads the cached row and
  skips translation + metric computation for that pair (`INSERT OR REPLACE`
  semantics on writes).

This makes runs **resumable**: if a run is interrupted halfway, re-running it
only processes the samples/models that were not completed. Delete the cache file
to force a full re-evaluation. The cache is git-ignored (`src/cache/.gitignore`).

---

## Output — Excel report

Each run writes a file named `<DD-MM-YYYY-HH-MM>_result.xlsx` into
`experiment.output_dir` (resolved from the working directory → `src/results/`).
The workbook is formatted with openpyxl: title and description rows, a styled
header at row 5, frozen panes, an auto-filter, alternating row colors and
auto-sized columns.

Result columns (as declared in `pipeline.define_header()`):

| Column                  | Description                                        |
| ----------------------- | -------------------------------------------------- |
| `sample_id`             | Corpus record id                                   |
| `timestamp`             | When the row was produced                          |
| `source_lang`           | Source language code                               |
| `target_lang`           | Target language code                               |
| `original_sentence`     | Input text                                         |
| `original_translation`  | Reference translation (`pt`)                       |
| `generated_translation` | Model output                                       |
| `model_name`            | Model id                                           |
| `BLEU` / `BERTscore` / `chrf` | Quality metric scores                    |
| `cpu_average_usage`, `cpu_samples`, `cpu_max_usage`, `cpu_min_usage` | CPU statistics |
| `additional_memory`, `initial_memory`, `final_memory`, `peak_memory` | Memory statistics |
| `inference_time`        | Wall-clock time of the translation call            |

> **Note (bug).** In `define_header()` the `"chrf"` literal is missing a
> trailing comma before the `# CPU` comment. Because Python concatenates
> adjacent string literals, the header currently renders as
> **`chrfcpu_average_usage`** (one column), and the real
> `cpu_average_usage` values are not written. See
> [Known limitations](#known-limitations).

---

## Supported models

| Family           | Hugging Face id                   | Language control            |
| ---------------- | --------------------------------- | --------------------------- |
| **Opus-MT**      | `Helsinki-NLP/opus-mt-tc-big-en-pt` | Fixed en→pt checkpoint (no language tokens) |
| **NLLB-200**     | `facebook/nllb-200-distilled-600M`  | FLORES codes (`eng_Latn` → `por_Latn`), forced via `forced_bos_token_id` |
| **M2M-100**      | `facebook/m2m100_418M`              | ISO codes, `src_lang` + `get_lang_id(target)` |

Each implementation extends the `BaseTranslationModel` ABC
(`src/models/translationModel.py`), which provides the shared configuration
(`device`, `precision`, `max_length`, `generation_params`) and a default batch
translation fallback. Loading follows the same pattern: instantiate the
tokenizer and model from the HF id, place on `cuda` (when available) or `cpu`,
and apply fp16 only on CUDA.

---

## Adding a new model

1. Create `src/models/impl/YourModel.py` with a class extending
   `BaseTranslationModel` implementing `load()` and `translate(...)`.
2. Register the Hugging Face id → class mapping in
   `ModelFactory.MODEL_CLASSES` (`src/models/factory/modelFactory.py`).
3. Add a `{ id, name }` entry to the `models` list in `model.yaml`
   (`name` must be the Hugging Face id).
4. Run — the validator will confirm the model exists on the Hub, and the
   factory will route it to your implementation.

> If the model needs different tokenizer/forward logic (e.g. FLORES codes for
> NLLB or `forced_bos_token_id`), mirror the approach in `NLLB.py` / `M2M100.py`.

---

## Running tests

Unit tests cover the YAML validator (no network): missing models, unsupported
metrics, invalid corpus lines, Hugging Face lookups and JSON→JSONL conversion.

```bash
pytest                 # from the project root
```

`tests/conftest.py` inserts `src/` into `sys.path`, and
`tests/test_validate_yaml.py` monkeypatches `_hf_model_exists` so the tests
never hit the network.

---

## Known limitations

- **Must run from `src/`.** `main.py`, `efficiency.py` and `common/`
  resolve `../model.yaml` from the current working directory. Reports and the
  cache are also written relative to the CWD. Always `cd src` first.
- **Quality metrics are not filtered.** The pipeline always computes BLEU,
  BERTScore and chrF for every sample; the `quality_metrics` section is only
  validated, and `comet` is accepted by the validator but has no
  implementation in `Metrics`.
- **Performance metrics are effectively bundled.** Enabling only a subset of
  `cpu_usage` / `memory_usage` / `inference_time` is not supported (aggregation
  always reads the three collectors). `gpu_utilization` is accepted by the
  validator but not yet implemented (the `nvidia-ml-py` dependency hints at
  future support).
- **`executions` is reserved.** The reproducibility settings
  (`quality_runs`, `seeds`, `performance_runs`, `performance_strategy`) are not
  consumed by the pipeline yet.
- **Excel header bug.** `"chrf"` is missing a comma in
  `pipeline.define_header()`, producing the merged header
  `chrfcpu_average_usage` and dropping the `cpu_average_usage` values from the
  report.
- **Incomplete `requirements.txt`.** `nltk` (BLEU) and `openpyxl` (Excel
  export) are imported at runtime but not listed — install them manually (see
  [Requirements](#requirements)).
- **Reference field hardcoded in row assembly.** `createCSV_model` reads
  `data["pt"]` for the reference translation rather than
  `dataset.target_lang`, so the report assumes a `pt` field even though
  translation itself honors the configured language pair.
- **BERTScore prints progress.** `score(..., verbose=True)` emits progress
  bars for every sentence, which makes the console output noisy on large
  corpora.
