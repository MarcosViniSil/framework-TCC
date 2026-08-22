import yaml

# Lendo o arquivo
with open('../../model.yaml', 'r', encoding='utf-8') as file:
    dados = yaml.safe_load(file)
    print(dados)

# Agora você pode acessar os campos
print(dados['experiment']['name'])
