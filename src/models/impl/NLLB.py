import torch
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
from domain.translationResult import TranslationResult
from models.translationModel import BaseTranslationModel

class NLLBModel(BaseTranslationModel):
    
    LANG_CODES = {
        'en': 'eng_Latn',
        'pt': 'por_Latn',
        'es': 'spa_Latn',
        'fr': 'fra_Latn',
        'de': 'deu_Latn',
        'it': 'ita_Latn'
    }
    
    def load(self):
        if not self._loaded:
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_name, 
                src_lang="eng_Latn"
            )
            self.model = AutoModelForSeq2SeqLM.from_pretrained(self.model_name)
            
            if self.device == 'auto':
                self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
            
            self.model.to(self.device)
            
            if self.precision == 'fp16' and self.device == 'cuda':
                self.model = self.model.half()
            
            self._loaded = True
        return self
    
    def _get_lang_code(self, lang: str) -> str:
        return self.LANG_CODES.get(lang, lang)
    
    def translate(self, text: str, source_lang: str = "en", target_lang: str = "pt") -> TranslationResult:
        if not self._loaded:
            self.load()
        
        source_code = self._get_lang_code(source_lang)
        target_code = self._get_lang_code(target_lang)
        
        self.tokenizer.src_lang = source_code
        
        inputs = self.tokenizer(
            text, 
            return_tensors="pt", 
            truncation=True, 
            max_length=self.max_length
        ).to(self.device)
        
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                forced_bos_token_id=self.tokenizer.lang_code_to_id[target_code],
                **self.generation_params,
                max_length=self.max_length
            )
        
        translated = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        return TranslationResult(
            source_text=text,
            target_text=translated,
            source_lang=source_lang,
            target_lang=target_lang,
            model_id=self.model_id
        )