from dataclasses import dataclass


@dataclass
class MetricResult:
    metric_name: str
    value: float
    metadata: dict
