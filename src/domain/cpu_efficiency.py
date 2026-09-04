from dataclasses import dataclass


@dataclass
class CpuEfficiency:
    average_usage: str
    samples: int
    max_usage: str
    min_usage: str
