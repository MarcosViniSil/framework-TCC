import torch
from transformers import M2M100ForConditionalGeneration, M2M100Tokenizer
from domain.translationResult import TranslationResult
from models.translationModel import BaseTranslationModel


class M2M100Model(BaseTranslationModel):
    
    def load(self):
        if not self._loaded:
            self.tokenizer = M2M100Tokenizer.from_pretrained(self.model_name)
            self.model = M2M100ForConditionalGeneration.from_pretrained(self.model_name)
            
            if self.device == 'auto':
                self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
            
            self.model.to(self.device)
            
            if self.precision == 'fp16' and self.device == 'cuda':
                self.model = self.model.half()
            
            self._loaded = True
        return self
    
    def translate(self, text: str, source_lang: str = "en", target_lang: str = "pt") -> TranslationResult:
        if not self._loaded:
            self.load()
        
        self.tokenizer.src_lang = source_lang
        
        inputs = self.tokenizer(
            text, 
            return_tensors="pt", 
            truncation=True, 
            max_length=self.max_length
        ).to(self.device)
        
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                forced_bos_token_id=self.tokenizer.get_lang_id(target_lang),
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