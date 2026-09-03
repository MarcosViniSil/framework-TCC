from dataclasses import dataclass

@dataclass
class CpuEfficiency:
    average_usage: float
    samples: int
    max_usage: float
    min_usage: float  