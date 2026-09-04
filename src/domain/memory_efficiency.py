from dataclasses import dataclass


@dataclass
class MemoryEfficiency:
    additional_memory: float
    initial_memory: float
    final_memory: float
    memory_peak: float
