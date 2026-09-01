from efficiency.efficiency import Efficiency


YAML_PATH = "../model.yaml"

def meu_metodo():
    # Simula trabalho pesado
    soma = sum(i * i for i in range(200_000_000))
    return soma

#validate_yaml_file(YAML_PATH)
#convert_corpus_to_dict(YAML_PATH)

ef = Efficiency()

ef.start_collection()

meu_metodo()

ef.stop_collection()
ef.collect_metrics()

#modelManager = ModelManager()
#models = Models.get_models_ids()
#translation = modelManager.translate("hello, world!",models[2])
#print(translation)