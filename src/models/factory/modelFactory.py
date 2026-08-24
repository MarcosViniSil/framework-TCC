from typing import Dict
from typing import List, Dict, Any
from models.translationModel import BaseTranslationModel
from models.impl.opusMT import OpusMTModel
from models.impl.NLLB import NLLBModel
from models.impl.M2M100 import M2M100Model


class ModelFactory:
        
    MODEL_CLASSES = {
        'opus_mt-200M': OpusMTModel,
        'nllb-600M': NLLBModel,
        'm2m100-418M': M2M100Model
    }
    
    @staticmethod
    def create_model(config: Dict[str, Any]) -> BaseTranslationModel:
        model_id = config.get('id')
        model_class = ModelFactory.MODEL_CLASSES.get(model_id)
        
        if model_class is None:
            raise ValueError(f"Model not supported: {model_id}")
        
        return model_class(config)