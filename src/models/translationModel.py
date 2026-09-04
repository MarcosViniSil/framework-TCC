from abc import ABC, abstractmethod
from typing import List, Dict, Any
from domain.translationResult import TranslationResult


class BaseTranslationModel(ABC):

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.model_id = config.get("id", "unknown")
        self.model_name = config.get("name")
        self.device = config.get("device", "auto")
        self.precision = config.get("precision", "fp16")
        self.max_length = config.get("max_length", 512)
        self.generation_params = config.get("generation_params", {})

        self.tokenizer = None
        self.model = None
        self._loaded = False

    @abstractmethod
    def load(self):
        pass

    @abstractmethod
    def translate(
        self, text: str, source_lang: str = "en", target_lang: str = "pt"
    ) -> TranslationResult:
        pass

    def translate_batch(
        self, texts: List[str], source_lang: str = "en", target_lang: str = "pt"
    ) -> List[TranslationResult]:
        return [self.translate(text, source_lang, target_lang) for text in texts]

    def is_loaded(self) -> bool:
        return self._loaded
