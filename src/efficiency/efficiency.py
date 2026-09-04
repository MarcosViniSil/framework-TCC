import os
import psutil
import yaml
import time
import threading

from domain.cpu_efficiency import CpuEfficiency
from domain.inference import Inference
from domain.memory_efficiency import MemoryEfficiency
from domain.efficiency import EfficiencyModel

YAML_PATH = "../model.yaml"


class Efficiency:

    def __init__(self):
        self.samples = []
        self.memory_samples = []

        self.libraries = []

        self.start_inference = None
        self.end_inference = None

        self.stop_event = None
        self.collector = None
        self.memory_collector = None

        self.process = psutil.Process(os.getpid())

        self.mem_before = None
        self.mem_after = None
        self.mem_peak = None

    def _get_libraries(self, yaml_path) -> list:
        with open(yaml_path, "r", encoding="utf-8") as file:
            data = yaml.safe_load(file)

        return data["performance_metrics"]

    def _collect_cpu_data(self, process, stop_event):

        while not stop_event.is_set():

            cpu_usage = process.cpu_percent(interval=0.05)

            cpu_usage = max(0, min(cpu_usage, 100))

            self.samples.append(cpu_usage)

            time.sleep(0.01)

    def _start_cpu_collection(self):

        self.stop_event = threading.Event()

        self.collector = threading.Thread(
            target=self._collect_cpu_data, args=(self.process, self.stop_event)
        )

        self.collector.start()

    def _stop_cpu_collection(self):

        self.stop_event.set()
        self.collector.join()

    def _get_memory_mb(self):

        return self.process.memory_info().rss / (1024 * 1024)

    def _collect_memory_data(self, stop_event):

        while not stop_event.is_set():

            memory = self._get_memory_mb()

            self.memory_samples.append(memory)

            time.sleep(0.01)

    def _start_memory_collection(self):

        self.memory_samples = []

        self.mem_before = self._get_memory_mb()

        self.memory_stop_event = threading.Event()

        self.memory_collector = threading.Thread(
            target=self._collect_memory_data, args=(self.memory_stop_event,)
        )

        self.memory_collector.start()

    def _stop_memory_collection(self):

        self.memory_stop_event.set()
        self.memory_collector.join()

        self.mem_after = self._get_memory_mb()

        if self.memory_samples:
            self.mem_peak = max(self.memory_samples)

    def _start_inference_collection(self):

        self.start_inference = time.perf_counter()

    def _stop_inference_collection(self):

        self.end_inference = time.perf_counter()

    def _memory_statistics(self) -> MemoryEfficiency:

        additional_memory = self.mem_peak - self.mem_before

        initial_memory = round(self.mem_before, 2)

        final_memory = round(self.mem_after, 2)

        memory_peak = round(self.mem_peak, 2)

        return MemoryEfficiency(
            additional_memory=additional_memory,
            initial_memory=initial_memory,
            final_memory=final_memory,
            memory_peak=memory_peak,
        )

    def _inference_statistic(self) -> Inference:

        elapsed = (self.end_inference - self.start_inference) * 1000

        return Inference(inferenceTime=round(elapsed, 2))

    def _cpu_statistics(self) -> CpuEfficiency:

        if not self.samples:
            return CpuEfficiency(samples=0, average_usage=0, max_usage=0, min_usage=0)

        average_usage = round(sum(self.samples) / len(self.samples), 2)

        sample_number = len(self.samples)

        max_usage = round(max(self.samples), 2)

        min_usage = round(min(self.samples), 2)

        max_usage = round(max(self.samples), 2)

        return CpuEfficiency(
            average_usage=average_usage,
            samples=sample_number,
            max_usage=max_usage,
            min_usage=min_usage,
        )

    def start_collection(self):

        libraries = self._get_libraries(YAML_PATH)

        for lib in libraries:

            if lib["name"] == "cpu_usage":
                self._start_cpu_collection()
                self.libraries.append("CPU")

            elif lib["name"] == "inference_time":
                self._start_inference_collection()
                self.libraries.append("INFERENCE_TIME")

            elif lib["name"] == "memory_usage":
                self._start_memory_collection()
                self.libraries.append("MEMORY_USAGE")

    def stop_collection(self):

        for lib in self.libraries:

            if lib == "CPU":
                self._stop_cpu_collection()

            elif lib == "INFERENCE_TIME":
                self._stop_inference_collection()

            elif lib == "MEMORY_USAGE":
                self._stop_memory_collection()

    def collect_metrics(self):

        cpu: CpuEfficiency = self._cpu_statistics()
        inference: Inference = self._inference_statistic()
        memory: MemoryEfficiency = self._memory_statistics()

        return EfficiencyModel(
            cpy_efficiency=cpu, memory_efficiency=memory, inference=inference
        )

    def clear(self):

        self.samples = []
        self.memory_samples = []
        self.libraries = []

        self.start_inference = None
        self.end_inference = None

        self.stop_event = None
        self.collector = None
        self.memory_collector = None

        self.mem_before = None
        self.mem_after = None
        self.mem_peak = None
