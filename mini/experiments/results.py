import os
import csv
from collections import defaultdict


def convert_results(hosts, results_dir, results_path, output_dir):
    print("Converting results")
    host_names = [host.name for host in hosts]
    node_dirs = os.scandir(output_dir)
    timers = defaultdict(list)

    for node_dir in node_dirs:
        if node_dir.name in host_names:
            output_path = node_dir.path + f'/log/results'
            with open(output_path,'r') as log_file:
                while line := log_file.readline():
                    timer_values = line.split()
                    timer_name = timer_values[0]
                    if len(timer_values) == 2:
                        start_time = timer_values[1]
                        timers[timer_name] = [start_time]
                    elif len(timer_values) == 3:
                        if timer_values[1] != "none":
                            start_time = timer_values[1]
                            end_time = timer_values[2]
                            timers[timer_name] = [start_time, end_time]
                        else:
                            end_time = timer_values[2]
                            if not timers[timer_name]:
                                timers[timer_name] = [0, end_time]
                            else:
                                timers[timer_name].append(end_time)

    with open(results_path,'w', newline='') as results_file:
        csv_writer = csv.DictWriter(results_file, fieldnames=['name', 'start', 'end', 'time'])
        csv_writer.writeheader()
        for name,values in timers.items():
            csv_writer.writerow({'name': name,'start': values[0],'end': values[1:],'time': [round((int(i) - int(values[0])) / 1000000) for i in values[1:]]})
