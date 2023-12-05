import re
from datetime import datetime
from statistics import mean, stdev
from types import NoneType
import matplotlib.pyplot as plt
import os.path
import csv
from os import listdir
from os.path import isfile, join

f = open('treino.csv', 'w')

writer = csv.writer(f)

windowSize = 100
windowSpeed = 5

def parse_entry(entry):
    match = re.search(r'\[(.*?)\]', entry)
    # timestamp, cpu_time, energy, sender_id, req_num, temp_val, pressure_val = ""
    if match:
        if entry[4] == ':':
            timestamp = datetime.strptime(entry[:9], '%H:%M:%S.%f')
        else:
            timestamp = datetime.strptime(entry[:9], '%M:%S.%f')
        id_num = int(re.search(r'ID:(\d+)', entry).group(1))
        if id_num == 1:
            sender_id = entry.split(':')
            sender_id = int(sender_id[-1], 16)
            cpu_time = re.search(r'CPU (\d+)', entry)
            packet_length = re.search(r'Packet length: (\d+)', entry)
            energy = re.search(r'Energy (\d+)', entry)
            req_num = re.search(r'No: (\d+)', entry)
            temp_val = re.search(r'Temperature: (\d+)', entry)
            pressure_val = re.search(r'Pressure: (\d+)', entry)
        else:
            return False
        return timestamp, cpu_time, packet_length, energy, req_num, temp_val, pressure_val, sender_id
    return None

def generate_crude_data(entries):
    data = {}
    for entry in entries:
        parsed_entry = parse_entry(entry)
        if parsed_entry:
            timestamp, cpu_time, packet_length, energy, req_num, temp_val, pressure_val, sender_id = parsed_entry
            if sender_id not in data:
                data[sender_id] = {'timestamps': [], 'cpu_time': [], 'packet_length': [], 'energy': [], 'req_num': [], 'temp_val': [], 'pressure_val': [], 'sender_id': [], 'freshness': []}
            if parsed_entry[0] != None: data[sender_id]['timestamps'].append(timestamp)
            if parsed_entry[1] != None: data[sender_id]['cpu_time'].append(int((cpu_time).group(1)))
            if parsed_entry[2] != None: data[sender_id]['packet_length'].append(int((packet_length).group(1)))
            if parsed_entry[3] != None: data[sender_id]['energy'].append(int((energy).group(1)))
            if parsed_entry[4] != None: 
                data[sender_id]['req_num'].append(int((req_num).group(1)))
                data[sender_id]['freshness'].append(data[sender_id]['timestamps'][-1].minute - (data[sender_id]['req_num'][-1] % 60)) 
            if parsed_entry[5] != None: data[sender_id]['temp_val'].append(int((temp_val).group(1)))
            if parsed_entry[6] != None: data[sender_id]['pressure_val'].append(int((pressure_val).group(1)))
            if parsed_entry[7] != None: data[sender_id]['sender_id'].append(sender_id)
    return data

def generate_data(entries, filename):
    data = {'timestamps': [], 'cpu_time': [], 'packet_length': [], 'energy': [], 'req_num': [], 'temp_val': [], 'pressure_val': [], 'sender_id': [], 'freshness': []}
    for entry in entries:
        parsed_entry = parse_entry(entry)
        if parsed_entry:
            timestamp, cpu_time, packet_length, energy, req_num, temp_val, pressure_val, sender_id = parsed_entry
            if parsed_entry[0] != None: data['timestamps'].append(timestamp)
            if parsed_entry[1] != None: data['cpu_time'].append(int((cpu_time).group(1)))
            if parsed_entry[2] != None: data['packet_length'].append(int((packet_length).group(1)))
            if parsed_entry[3] != None: data['energy'].append(int((energy).group(1)))
            if parsed_entry[4] != None: 
                data['req_num'].append(int((req_num).group(1)))
                data['freshness'].append(60*data['timestamps'][-1].hour + data['timestamps'][-1].minute - (data['req_num'][-1])) 
            if parsed_entry[5] != None: data['temp_val'].append(int((temp_val).group(1)))
            if parsed_entry[6] != None: data['pressure_val'].append(int((pressure_val).group(1)))
            if parsed_entry[7] != None: data['sender_id'].append(sender_id)
    
    list = ['cpu_time', 'packet_length','energy', 'req_num', 'freshness', 'temp_val', 'pressure_val']
    for item in list:
        data[item+'_mean'] = 0
        data[item+'_stdev'] = 0
        if len(data[item]) > 0:
            data[item+'_mean'] = mean(data[item])
        if len(data[item]) > 1:
            data[item+'_stdev'] = stdev(data[item])
    
    #get_mean_datetime
    meanTime = data['timestamps'][0] + ((data['timestamps'][-1] - data['timestamps'][0])/2)

    atkTime = re.findall(r'\d+', filename)[-1]

    if (60*meanTime.hour + meanTime.minute > int(atkTime)) and ("NodesNormal" not in filename): 
        data['classification'] = 1
    else: 
        data['classification'] = 0
    
    data['mean_time'] = meanTime.timestamp()

    data['number_of_clients'] = len(set(data['sender_id']))

    return data
            
def read_file(filename):
    with open(os.getcwd() + '/trainset/' + filename, 'r') as file:
        lines = file.readlines()
        lines = [line.strip() for line in lines]  
    return lines

wantedValues = ["mean_time", "cpu_time_mean", "cpu_time_stdev", 
                "packet_length_mean", "packet_length_stdev", 
                "energy_mean", "energy_stdev", 
                "req_num_stdev", 
                "freshness_mean", "freshness_stdev", 
                "temp_val_mean", "temp_val_stdev", 
                "pressure_val_mean", "pressure_val_stdev",
                "number_of_clients", "classification"]

# wantedValues = ["mean_time",  
#                 "packet_length_mean", "packet_length_stdev", 
#                 "energy_mean", "energy_stdev",  
#                 "freshness_mean", "freshness_stdev", 
#                 "number_of_clients", "classification"]

# writer.writerow(wantedValues)

filelist = [f for f in listdir(os.getcwd()+'/trainset') if isfile(join(os.getcwd()+'/trainset', f))]

for file in filelist:
    lines = read_file(file)
    data = []
    for i in range (int(len(lines)/windowSpeed)-windowSize):
        lineTemp = lines[windowSpeed*i:(windowSpeed*i)+windowSize]
        data.append(generate_data(lineTemp,file))
        dataCsv = []
        for value in wantedValues:
            dataCsv.append(data[i][value])
        writer.writerow(dataCsv)

data

# g
# enerate_data(lines)
