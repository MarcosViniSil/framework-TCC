import psutil
import time
import os

def meu_metodo():
    # Simula trabalho pesado
    soma = sum(i * i for i in range(2000))
    return soma

# Pega o PID do processo atual
pid = os.getpid()
process = psutil.Process(pid)

# Amostras antes de executar
amostras = []

# Executa o método e coleta amostras de CPU a cada 0.1s
inicio = time.time()
while time.time() - inicio < 0.1:  # Pequena pausa inicial
    pass

# Função para coletar amostras durante a execução
def coletar_cpu(process, amostras, stop_event):
    while not stop_event.is_set():
        uso_cpu = process.cpu_percent(interval=0.05)  # intervalo de 50ms
        amostras.append(uso_cpu)
        time.sleep(0.01)

import threading
stop_event = threading.Event()
coletor = threading.Thread(target=coletar_cpu, args=(process, amostras, stop_event))
coletor.start()

# Executa o método
resultado = meu_metodo()

# Para a coleta
stop_event.set()
coletor.join()

# Calcula a média
if amostras:
    media_cpu = sum(amostras) / len(amostras)
    print(f"Uso médio de CPU durante a execução: {media_cpu:.2f}%")
    print(f"Número de amostras: {len(amostras)}")
    print(f"Uso máximo: {max(amostras):.2f}%")
    print(f"Uso mínimo: {min(amostras):.2f}%")
else:
    print("Nenhuma amostra coletada")