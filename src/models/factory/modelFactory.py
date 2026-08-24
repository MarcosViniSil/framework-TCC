from typing import Dict, Any
from common.models import Models
from models.translationModel import BaseTranslationModel
from models.impl.opusMT import OpusMTModel
from models.impl.NLLB import NLLBModel
from models.impl.M2M100 import M2M100Model


class ModelFactory:
        
    MODEL_CLASSES = {
        'Helsinki-NLP/opus-mt-tc-big-en-pt': OpusMTModel,
        'facebook/nllb-200-distilled-600M': NLLBModel,
        'facebook/m2m100_418M': M2M100Model
    }
    
    @staticmethod
    def create_model(modelId: str) -> BaseTranslationModel:
        model_class = ModelFactory.MODEL_CLASSES.get(modelId)
        if model_class is None:
            raise ValueError(f"Model not supported: {modelId}")
        config = Models.get_model_details(modelId)
        return model_class(config)