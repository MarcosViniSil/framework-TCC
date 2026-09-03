from dataclasses import dataclass

from domain.cpu_efficiency import CpuEfficiency
from domain.inference import Inference
from domain.memory_efficiency import MemoryEfficiency

@dataclass
class EfficiencyModel:
    cpy_efficiency: CpuEfficiency
    memory_efficiency: MemoryEfficiency
    inference:Inference