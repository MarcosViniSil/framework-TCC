from typing import List, Dict, Any, Optional
from common.models import Models
from models.translationModel import BaseTranslationModel, TranslationResult
from models.factory.modelFactory import ModelFactory

class ModelManager:    
    def __init__(self):
        self.models: Dict[str, BaseTranslationModel] = {}
        self.current_model_id: Optional[str] = None
        self.models_config = Models.get_models()


    def _load_model(self, model_id: str) -> BaseTranslationModel:
        if model_id in self.models:
            return self.models[model_id]

        model = ModelFactory.create_model(model_id)
        model.load()
        self.models[model_id] = model
        self.current_model_id = model_id

        return model

    
    def _get_model(self, model_id: Optional[str] = None) -> BaseTranslationModel:
        if model_id is None:
            model_id = self.current_model_id
        
        if model_id is None:
            raise ValueError("None model selected")
        
        return self._load_model(model_id)

    
    def translate(self,text: str,model_id: Optional[str] = None,source_lang: str = "en",    target_lang: str = "pt") -> TranslationResult:

        model = self._get_model(model_id)
        print("model ",model)
        return model.translate(text, source_lang, target_lang)
    
    def translate_batch(self,texts: List[str],model_id: Optional[str] = None,source_lang:   str = "en",target_lang: str = "pt") -> List[TranslationResult]:
        model = self._get_model(model_id)
        return model.translate_batch(texts, source_lang, target_lang)
    
    def get_available_models(self) -> List[Dict[str, Any]]:
        return self.models_config
    
    def get_model_names(self) -> List[str]:
        return [m.get('id') for m in self.models_config]