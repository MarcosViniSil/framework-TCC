import os
import psutil
import yaml
import time
import threading
import tracemalloc


YAML_PATH = "../model.yaml"

class Efficiency:
    def __init__(self):
        self.samples = []
        self.libraries = []
        self.start_inference = None
        self.end_inference = None
        self.stop_event = None
        self.collector = None
        self.process = None
        self.mem_before = None
        self.mem_after = None
        

    def _get_libraries(self,yaml_path) -> str:
        with open(yaml_path, 'r', encoding='utf-8') as file:
            data = yaml.safe_load(file)

            return data['performance_metrics']


    def _collect_cpu_data(self,process, stop_event):
        while not stop_event.is_set():
            cpu_usage = process.cpu_percent(interval=0.05)
            if cpu_usage < 0:
                cpu_usage = 0
            if cpu_usage > 100:
                cpu_usage = 100
            self.samples.append(cpu_usage)
            time.sleep(0.01)

    def _start_cpu_collection(self) -> None:

        pid = os.getpid()
        process = psutil.Process(pid)

        start = time.time()
        while time.time() - start < 0.1:  
            pass

        self.stop_event = threading.Event()
        self.collector = threading.Thread(target=self._collect_cpu_data, args=(process, self.stop_event))

        self.collector.start()

    def _start_memory_collection(self) -> None:
        tracemalloc.start()
        self.mem_before = tracemalloc.take_snapshot()

    def _stop_memory_collection(self) -> None:
        self.mem_after = tracemalloc.take_snapshot()
        tracemalloc.stop()

    def _start_inference_collection(self) -> None:
        self.start_inference = time.perf_counter()

    def _stop_inference_collection(self) -> None:
        self.end_inference = time.perf_counter()

    def _stop_cpu_collection(self) -> None:
        self.stop_event.set()
        self.collector.join()

    def _memory_statistics(self) -> None:
        stats = self.mem_before.compare_to(self.mem_after, 'lineno')
        total_diff = sum(stat.size_diff for stat in stats)
        total_diff_mb = total_diff / (1024 * 1024)
    
        print(f"Memória adicional consumida: {total_diff_mb:.2f} MB")

    def _inference_statistic(self) -> None:
        print(f"Tempo de inferencia , {(self.end_inference - self.start_inference) * 1000:.2f} ms" )

    def _cpu_statistics(self) -> None:
       if self.samples:

        cpu_average_usage = sum(self.samples) / len(self.samples)
        print(f"Uso médio de CPU durante a execução: {cpu_average_usage:.2f}%")
        print(f"Número de amostras: {len(self.samples)}")
        print(f"Uso máximo: {max(self.samples):.2f}%")
        print(f"Uso mínimo: {min(self.samples):.2f}%")

       else:
            print("Nenhuma amostra coletada") 

    def start_collection(self) -> None:
        libraries = self._get_libraries(YAML_PATH)

        for lib in libraries:
            if lib['name'] == "cpu_usage":
                self._start_cpu_collection()
                self.libraries.append("CPU")
            if lib['name'] == "inference_time":
                self._start_inference_collection()
                self.libraries.append("INFERENCE_TIME")
            if lib['name'] == "memory_usage":
                self._start_memory_collection()
                self.libraries.append("MEMORY_USAGE")

    def stop_collection(self) -> None:
        for lib in self.libraries:
            if lib == "CPU":
                self._stop_cpu_collection()
            if lib == "INFERENCE_TIME":
                self._stop_inference_collection()
            if lib == "MEMORY_USAGE":
                self._stop_memory_collection()


    def collect_metrics(self) -> None:
        self._cpu_statistics()
        self._inference_statistic()
        self._memory_statistics()

    def clear(self) -> None:
        self.samples = []
        self.libraries = []
        self.start_inference = None
        self.end_inference = None
        self.stop_event = None
        self.collector = None
        self.process = None
        self.mem_before = None
        self.mem_after = None