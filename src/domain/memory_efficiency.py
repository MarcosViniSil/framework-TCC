from dataclasses import dataclass


@dataclass
class MemoryEfficiency:
    additional_memory: str
    initial_memory: str
    final_memory: str
    memory_peak: str
