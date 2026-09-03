from dataclasses import dataclass


@dataclass
class TranslationResult:
    source_text: str
    target_text: str
    source_lang: str = "en"
    target_lang: str = "pt"
    model_id: str = ""
    
    def __str__(self):
        return {self.target_text}