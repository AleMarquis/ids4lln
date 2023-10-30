import re
from datetime import datetime
from types import NoneType
import matplotlib.pyplot as plt
import os.path

plt.rcParams['legend.title_fontsize'] = 'xx-small'

def parse_entry(entry):
    match = re.search(r'\[(.*?)\]', entry)
    if match:
        if entry[7] == '.':
            timestamp = datetime.strptime(entry[:9], '%H:%M:%S.%f')
        else:
            timestamp = datetime.strptime(entry[:9], '%M:%S.%f')
        id_num = int(re.search(r'ID:(\d+)', entry).group(1))
        temp = re.search(r'Tx/Rx/MissedTx: (\d+)/(\d+)/(\d+)', entry)
        if temp:
            tx = int(temp.group(1))
            rx = int(temp.group(2))
        else:
            return False
        return timestamp, id_num, rx
    return None

def generate_graph(entries):
    data = {}
    for entry in entries:
        parsed_entry = parse_entry(entry)
        if parsed_entry:
            timestamp, id_num, tx = parsed_entry
            if id_num not in data:
                data[id_num] = {'timestamps': [], 'tx': []}
            data[id_num]['id'] = (id_num)
            data[id_num]['tx'] = (tx)

    # TODO: Mudar as cores para escala cinza, diferenciar atacante 
    plt.figure(figsize=(10, 6))
    for i in range (1, 33):
        for id_num, values in data.items():
            if id_num == i:
                if values['id'] % 4 != 0:
                    data[id_num]['color'] = '#bfbfbf'
                else:
                    data[id_num]['color'] = '#4d4d4d'
                plt.bar(values['id'], values['tx'], label=f'ID: {id_num}', color = values['color'])
                break

    plt.xlabel('ID do nó', fontsize=20)
    plt.ylabel('Número de requisições concluídas', fontsize=20)

    plt.xticks(fontsize=14)
    plt.yticks(fontsize=20)

    plt.title('')
    #plt.yscale('log')
    #plt.legend(fontsize='12', ncol=2)
    plt.show()

# Exemplo de entradas
def read_file(filename):
    with open(os.getcwd() + '/Logs - RSSF/' + filename, 'r') as file:
        lines = file.readlines()
        lines = [line.strip() for line in lines]  # Remove os espaços em branco no início e no fim de cada linha
    return lines

# Exemplo de uso
filename = 'loglistener4Blackhole.txt'  # Substitua pelo caminho correto para o arquivo
lines = read_file(filename)

generate_graph(lines)