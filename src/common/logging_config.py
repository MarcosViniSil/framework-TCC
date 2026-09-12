"""Centralised logging configuration.

Third-party libraries (transformers, torch, huggingface_hub, bert_score, ...)
are noisy on the console. This module downgrades them to ERROR so only their
real failures surface, while the framework's own warnings/errors stay visible.
"""

from __future__ import annotations

import logging
import os
import warnings

# These must be set before transformers / huggingface_hub are imported: both read
# them while building their module-level state (progress bars, verbosity).
_QUIET_ENV_VARS = {
    "TRANSFORMERS_VERBOSITY": "error",
    "HF_HUB_DISABLE_PROGRESS_BARS": "1",
    "HF_HUB_DISABLE_TELEMETRY": "1",
    "TOKENIZERS_PARALLELISM": "false",
}

for _name, _value in _QUIET_ENV_VARS.items():
    os.environ.setdefault(_name, _value)

# Third-party loggers restricted to ERROR (everything below is discarded).
_NOISY_LOGGERS = (
    "transformers",
    "huggingface_hub",
    "tokenizers",
    "torch",
    "nltk",
    "sacrebleu",
    "bert_score",
    "datasets",
    "sentencepiece",
    "matplotlib",
    "PIL",
    "urllib3",
    "filelock",
    "httpx",
    "httpcore",
)


def configure_logging() -> None:
    """Show only ERROR-level records coming from third-party libraries."""
    logging.basicConfig(level=logging.WARNING, format="%(levelname)s: %(message)s")

    for name in _NOISY_LOGGERS:
        logging.getLogger(name).setLevel(logging.ERROR)

    # Benign LibreSSL/OpenSSL notice raised by urllib3 on some macOS setups.
    warnings.filterwarnings("ignore", message=".*urllib3 v2 only supports.*")

    try:
        from transformers.utils import logging as transformers_logging
    except ImportError:
        return

    transformers_logging.set_verbosity_error()
    transformers_logging.disable_progress_bar()
