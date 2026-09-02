from common.models import Models
from dataset.load_dataset import convert_corpus_to_dict
from efficiency.efficiency import Efficiency
from models.modelManager import ModelManager
import csv
from datetime import datetime

YAML_PATH = "../model.yaml"

def meu_metodo():
    # Simula trabalho pesado
    soma = sum(i * i for i in range(200_000))
    return soma

#validate_yaml_file(YAML_PATH)
#convert_corpus_to_dict(YAML_PATH)

ef = Efficiency()

#ef.start_collection()
#
#meu_metodo()
#
#ef.stop_collection()
#ef.collect_metrics()

dataset = convert_corpus_to_dict(YAML_PATH)

data_to_csv = [] 

modelManager = ModelManager()
models = Models.get_models_ids()

for data in dataset.corpus:
    ef.start_collection()
    translation = modelManager.translate(data['en'],models[2])
    print("id ",data['id'], " original ",data['en'], " translation ",translation)
    data_to_csv.append({
        'timestamp': datetime.now(),
        'id':data['id'],
        'original':data['en'],
        'translation': translation,
        'model_name':models[2]
    })
    ef.stop_collection()
    ef.collect_metrics()

    ef.clear()

with open('traducoes.csv', 'w', newline='', encoding='utf-8') as arquivo:
    writer = csv.writer(arquivo)
    
    # Escreve o cabeçalho
    writer.writerow(['timestamp','id', 'original', 'translation','model_name'])
    
    # Escreve os dados
    for data in data_to_csv:
        writer.writerow([data['timestamp'],data['id'], data['original'], data['translation'], data['model_name']])

