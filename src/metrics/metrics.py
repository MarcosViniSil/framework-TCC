from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
from bert_score import score
import sacrebleu

from domain.metrics import MetricResult


class Metrics:

    def __init__(self):
        pass

    def bleu(self, reference: str, generated_by_model: str) -> MetricResult:
        if not reference or not generated_by_model:
            raise ValueError(
                "Cannot calculate bleu because either "
                "reference or generated_by_model is empty"
            )

        reference_tokens = reference.split()
        generated_tokens = generated_by_model.split()

        smooth = SmoothingFunction().method1

        bleu_value = sentence_bleu(
            [reference_tokens], generated_tokens, smoothing_function=smooth
        )

        return MetricResult(metric_name="BLEU", value=float(bleu_value), metadata=None)

    def BERTscore(self, reference: str, generated_by_model: str) -> MetricResult:
        if not reference or not generated_by_model:
            raise ValueError(
                "Cannot calculate bleu because either "
                "reference or generated_by_model is empty"
            )

        precision, recall, f1 = score(
            [generated_by_model], [reference], lang="pt", verbose=True
        )

        return MetricResult(
            metric_name="BERTscore", value=float(f1.mean()), metadata=None
        )

    def chrf(self, reference: str, generated_by_model: str) -> MetricResult:
        if not reference or not generated_by_model:
            raise ValueError(
                "Cannot calculate bleu because either "
                "reference or generated_by_model is empty"
            )

        chrf = sacrebleu.sentence_chrf(generated_by_model, [reference])

        return MetricResult(metric_name="chrf", value=float(chrf.score), metadata=None)
