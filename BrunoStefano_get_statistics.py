# -*- coding: iso8859-1 -*-

import colorsys
import os
import re, sys
from collections import defaultdict
import matplotlib as mpl
import matplotlib.pyplot as plt
import math
import numpy as np
import scipy.stats
import itertools
from statistics import mean
mpl.rcParams.update(mpl.rcParamsDefault)


# Delay and delivery statistics will be calculated considering each retransmission
# as a new transmission
STAT_CALC = "Individual"
# Delay and delivery statistics will be calculated considering each retransmission
# as part of the initial transmission
# STAT_CALC = "E2E"

# STAT_DESV = "STD_DEV"
STAT_DESV = "CONF_INTERVAL"
STAT_CONFIDENCE = 0.95


def parse_file(simulation_path, simulations_metrics):
    cooja_output = ""
    print("Parsing", simulation_path+"/"+cooja_output)
    simulation_number = simulation_path.split("_")[-1]
    
    tx_per_node = defaultdict(defaultdict)
    tx_by_time = defaultdict(int)
    tx_total = 0
    tx_missed_per_node = defaultdict(defaultdict)
    tx_missed_by_time = defaultdict(int)
    tx_missed_total = 0
    retx = {}
    rx_per_node = defaultdict(defaultdict)
    rx_by_time = defaultdict(int)
    rx_total =0
    txb = defaultdict(list)
    txb = {}
    fg_time = -1
    energy_consumption = defaultdict(defaultdict)
    battery_level = defaultdict(defaultdict)
    dead_nodes = []


        
    with open(os.path.join(simulation_path), "r") as f:

        for l in f:
            
            if "Energy Consumption:" in l:
                line_fields = l.split()
                time = line_fields[0]
                time = int(int(time)/1000000)
                node = line_fields[1]
                energy = int(line_fields[-2])
                energy_consumption[node][time] = energy
            
            if "Battery level:" in l:
                line_fields = l.split()
                time = line_fields[0]
                time = int(int(time)/1000000)
                node = line_fields[1]
                battery = line_fields[-3]
                battery = int(battery)*100/255
                battery_level[node][time] = battery

            if "Tx:" in l:
                line_fields = l.split()
                time = line_fields[0]
                time = re.sub('[:.;]', '', time)
                time = int(int(time)/1000000)
                node = line_fields[1]
                tx = int(line_fields[6][0])
                tx_per_node[node][time] = tx
                if(tx_per_node[node].values().__len__() < 2):
                    tx_total += tx
                    tx_by_time[time] = tx_total
                else:
                    tx_increase = list(tx_per_node[node].values())[-1] - list(tx_per_node[node].values())[-2]
                    tx_total += tx_increase
                    tx_by_time[time] = tx_total

            if "Tx Missed:" in l:
                line_fields = l.split()
                time = line_fields[0]
                time = int(int(time)/1000000)
                node = line_fields[1]
                tx_missed = int(line_fields[-1])
                tx_missed_per_node[node][time] = tx_missed
                if(tx_missed_per_node[node].values().__len__() < 2):
                    tx_missed_total += tx_missed
                    tx_missed_by_time[time] = tx_missed_total
                else:
                    tx_missed_increase = list(tx_missed_per_node[node].values())[-1] - list(tx_missed_per_node[node].values())[-2]
                    tx_missed_total += tx_missed_increase
                    tx_missed_by_time[time] = tx_missed_total
            
            if "Rx:" in l:
                line_fields = l.split()
                time = line_fields[0]
                time = int(int(time)/1000000)
                node = line_fields[1]
                rx = int(line_fields[-1])
                rx_per_node[node][time] = rx
                if(rx_per_node[node].values().__len__() < 2):
                    rx_total += rx
                    rx_by_time[time] = rx_total
                else:
                    rx_increase = list(rx_per_node[node].values())[-1] - list(rx_per_node[node].values())[-2]
                    rx_total += rx_increase
                    rx_by_time[time] = rx_total

            if "Received SHUTDOWN" in l:
                line_fields = l.split()
                node = line_fields[1]
                dead_nodes.append(node)


    marker = itertools.cycle(('o', 'v', '^', '<', '>', 's', '8', 'p'))

    plt.rcParams['text.usetex'] = False
    plt.rcParams['font.size'] = 16

    if(energy_consumption.items().__len__() > 0):
        plt.figure()
        for node_id, node_info in energy_consumption.items():
            plt.plot(node_info.keys(), node_info.values(), marker.__next__(), linestyle = '-', label = "node {}".format(node_id))

        plt.title("Energy consumption per node")
        plt.xlabel('Time (s)')
        plt.ylabel('Consumed energy (mJ)')
        plt.legend()
        #plt.show()
        plt.savefig('/energy.png', format='png', bbox_inches='tight')
        plt.close()

    if(battery_level.items().__len__() > 0):
        plt.figure()
        for node_id, node_info in battery_level.items():
            plt.plot(node_info.keys(), node_info.values(), marker.__next__(), linestyle = '-', label = "node {}".format(node_id))

        plt.title("Battery level per node")
        plt.xlabel('Time (s)')
        plt.ylabel('Battery level (%)')
        plt.legend()
        #plt.show()
        plt.savefig('/battery.png', format='png', bbox_inches='tight')
        plt.close()

    dict_keys = list(tx_missed_per_node.keys())
    dict_keys = [int(x) for x in dict_keys]
    dict_keys.sort()
    dict_keys = [str(x) for x in dict_keys]
    tx_missed_per_node = {i: tx_missed_per_node[i] for i in dict_keys}

    if(tx_missed_per_node.items().__len__() > 0):
        plt.figure()
        last_tx_missed_per_node = []
        for node_id, node_info in tx_missed_per_node.items():
            last_tx_missed_per_node.append(list(node_info.values())[-1])
            plt.plot(node_info.keys(), node_info.values(), marker.__next__(), linestyle = '-', label = "no {}".format(node_id))

        simulations_metrics[simulation_number]["tx_missed"] = round(mean(last_tx_missed_per_node),2)

        plt.title("Transmissoes perdidas por no")
        plt.xlabel('Tenpo (s)')
        plt.ylabel('Transmissoes perdidas')
        plt.legend(fontsize = 'xx-small')
        #plt.show()
        plt.savefig('/tx_missed_per_node.png', format='png', bbox_inches='tight')
        plt.close()
    

    dict_keys = list(tx_per_node.keys())
    dict_keys = [int(x[3:]) for x in dict_keys]
    dict_keys.sort()
    dict_keys = [str(x) for x in dict_keys]
    tx_per_node = {i: tx_per_node[i] for i in dict_keys}

    if(tx_per_node.items().__len__() > 0):
        plt.figure()
        for node_id, node_info in tx_per_node.items():
            plt.plot(node_info.keys(), node_info.values(), marker.__next__(), linestyle = '-', label = "no {}".format(node_id))

        plt.title("Transmissoes por no")
        plt.xlabel('Tempo (s)')
        plt.ylabel('Mensagens enviadas')
        plt.legend(fontsize = 'xx-small')
        plt.show()
        #plt.savefig('tx_per_node.png', format='png', bbox_inches='tight')
        plt.close()

    dict_keys = list(rx_per_node.keys())
    dict_keys = [int(x) for x in dict_keys]
    dict_keys.sort()
    dict_keys = [str(x) for x in dict_keys]
    rx_per_node = {i: rx_per_node[i] for i in dict_keys}

    if(rx_per_node.items().__len__() > 0):
        plt.figure()
        for node_id, node_info in rx_per_node.items():
            plt.plot(node_info.keys(), node_info.values(), marker.__next__(), linestyle = '-', label = "node {}".format(node_id))

        plt.title("Rx per node")
        plt.xlabel('Time (s)')
        plt.ylabel('Messages received')
        plt.legend(fontsize = 'xx-small')
        #plt.show()
        plt.savefig('/rx_per_node.png', format='png', bbox_inches='tight')
        plt.close()

    if(tx_by_time.items().__len__() > 0):
        plt.figure()
        plt.plot(tx_by_time.keys(), tx_by_time.values(), ",", linestyle = '-', label = "Total Tx")

        plt.title("Total Tx")
        plt.xlabel('Time (s)')
        plt.ylabel('Messages sent')
        plt.legend()
        plt.show()
        plt.savefig('tx_total.png', format='png', bbox_inches='tight')
        plt.close()

    if(rx_by_time.items().__len__() > 0):
        plt.figure()
        plt.plot(rx_by_time.keys(), rx_by_time.values(), ",", linestyle = '-', label = "Total Rx")

        plt.title("Total Rx")
        plt.xlabel('Time (s)')
        plt.ylabel('Messages received')
        plt.legend()
        #plt.show()
        plt.savefig('/rx_total.png', format='png', bbox_inches='tight')
        plt.close()

    if(tx_per_node.items().__len__() > 0 and rx_per_node.items().__len__() > 0):
        plt.figure()
        packet_delivery_rate_per_node = {}
        for node_id, node_info in rx_per_node.items():
            if node_id in dead_nodes or (int(node_id) > 40 and int(simulation_number) != 5):
                continue
            last_stamp_tx = list(tx_per_node[node_id].keys())[-1]
            last_stamp_tx_missed = list(tx_missed_per_node[node_id].keys())[-1]
            last_stamp_rx = list(node_info.keys())[-1]
            last_tx = tx_per_node[node_id][last_stamp_tx]
            last_tx_missed = tx_missed_per_node[node_id][last_stamp_tx_missed]
            last_tx = last_tx + last_tx_missed
            last_rx = rx_per_node[node_id][last_stamp_rx]
            if last_tx == 0:
                packet_delivery_rate = 0
            else:
                packet_delivery_rate = last_rx/last_tx
            packet_delivery_rate_per_node[node_id] = round(packet_delivery_rate * 100, 2)
        

        simulations_metrics[simulation_number]["packet_delivery_rate"] = round(mean(list(packet_delivery_rate_per_node.values())),2)

        plt.bar(packet_delivery_rate_per_node.keys(), packet_delivery_rate_per_node.values())

        plt.title("Packet delivery rate (PDR) per node")
        plt.xlabel('Node')
        plt.ylabel('PDR (%)')
        plt.legend()
        plt.ylim(80, 100)  
        #plt.show()
        plt.savefig('/packet_delivery_rate.png', format='png', bbox_inches='tight')
        plt.close()

def generate_plots(simulations_metrics, metrics_path):
    fig, ax = plt.subplots()
    bar_labels = ['0', '2', '4', '6', '8']
    colors = ['tab:cyan', 'tab:blue', 'tab:purple', 'tab:red', 'tab:pink', 'tab:orange', 'tab:green', 'tab:olive',  'tab:brown',  'tab:gray']
    patterns = [ "|" , "\\" , "/" , "+" , "-", ".", "*","x", "o", "O" ]

    packet_delivery_rate_per_simulation = {}
    for simulation_number, simulation_metrics in simulations_metrics.items():
        if "packet_delivery_rate" in simulation_metrics.keys():
            packet_delivery_rate_per_simulation[simulation_number] = simulation_metrics["packet_delivery_rate"]
            print(simulation_number, simulation_metrics["packet_delivery_rate"])



    ax.bar(bar_labels, packet_delivery_rate_per_simulation.values(), label=bar_labels, color=colors[0:packet_delivery_rate_per_simulation.__len__()], hatch=patterns[0:packet_delivery_rate_per_simulation.__len__()])

    ax.set_ylabel('Taxa de entrega de pacotes (%)')
    ax.set_xlabel('Quantidades de nos desligados na simulacao')
    ax.set_title('Media da taxa de entrega de pacotes por no por simulacao')
    #ax.legend()
    ax.set_ylim(60, 100) 
    fig.savefig(metrics_path+'/average_packet_delivery_rate.png', format='png', bbox_inches='tight')
    plt.close()

    fig, ax = plt.subplots()

    tx_missed_per_simulation = {}
    for simulation_number, simulation_metrics in simulations_metrics.items():
        if "tx_missed" in simulation_metrics.keys():
            tx_missed_per_simulation[simulation_number] = simulation_metrics["tx_missed"]
            print(simulation_number, simulation_metrics["tx_missed"])




    ax.bar(bar_labels, tx_missed_per_simulation.values(), label=bar_labels, color=colors[0:tx_missed_per_simulation.__len__()], hatch=patterns[0:tx_missed_per_simulation.__len__()])

    ax.set_ylabel('Transmissoes perdidas')
    ax.set_xlabel('Quantidades de nos desligados na simulacao')
    ax.set_title('Media de transmissoes perdidas por no por simulacao')
    #ax.legend()
    ax.set_ylim(0, 60) 
    fig.savefig(metrics_path+'/tx_missed_per_simulation.png', format='png', bbox_inches='tight')
    plt.close()

    # plt.bar(packet_delivery_rate_per_simulation.keys(), packet_delivery_rate_per_simulation.values(), colours)
    # plt.title("Average packet delivery rate (PDR) per Simulation")
    # plt.xlabel('Simulation')
    # plt.ylabel('PDR (\%)')
    # plt.legend()
    # plt.ylim(0, 100)  
    # #plt.show()
    # plt.savefig(metrics_path+'/average_packet_delivery_rate.png', format='png', bbox_inches='tight')
    # plt.close()




if __name__ == "__main__":
    simulations_metrics = defaultdict(defaultdict)
    SELF_PATH = os.path.dirname(os.path.abspath(__file__))
    n_agrs = len(sys.argv)
    if n_agrs > 1:
        for simulation in sys.argv[1:]:
            simulation_path = "simulation_{}".format(simulation)
            simulation_path = os.path.join(SELF_PATH, simulation_path)

            #try:
            parse_file(simulation_path, simulations_metrics)
            #except:
            #    print("problem parsing", simulation_path)

    else:
        self_path_files = os.listdir(SELF_PATH)
        simulation_paths = []
        for f in self_path_files:
            if f.startswith("loglistener"):
                simulation_paths.append(f)
        
        

        for simulation_path in simulation_paths:
            simulation_path = os.path.join(SELF_PATH, simulation_path)

            #try:
            parse_file(simulation_path, simulations_metrics)
            #except:
            #    print("problem parsing", simulation_path)
    
    generate_plots(simulations_metrics, SELF_PATH)

