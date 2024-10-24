import os
import csv
from collections import defaultdict
import statistics
import re
import numpy as np


def convert_results(hosts, results_dir, results_path, output_dir):
    print(f"Logging results to {results_path}")
    host_names = [host.name for host in hosts]
    node_dirs = os.scandir(output_dir)
    timers = defaultdict(list)

    for node_dir in node_dirs:
        if node_dir.name in host_names:
            output_path = node_dir.path + f'/log/results'
            with open(output_path, 'r') as output_file:
                while line := output_file.readline():
                    timer_values = line.split()
                    if len(timer_values) < 2:
                        print(line)
                        raise Exception("Missing result")
                    timer_name = timer_values[0]
                    if timer_values[1] == 'none':
                        timers[timer_name].append(timer_values[2])
                    else:
                        if len(timer_values) > 2:
                            timers[timer_name].append(timer_values[1])
                            timers[timer_name].append(timer_values[2])
                        else:
                            timers[timer_name] = [timer_values[1]] + timers[timer_name]

    with open(results_path,'x', newline='') as results_file:
        csv_writer = csv.DictWriter(results_file, fieldnames=['name', 'start', 'end', 'time'])
        csv_writer.writeheader()
        for name,values in timers.items():
            csv_writer.writerow({'name': name,'start': values[0],'end': values[1:],'time': ",".join([str((float(i) - float(values[0])) / 1000000) for i in values[1:]])})


def analyse_results(results_dir, analysis_file):
    with open(f"{results_dir}/" + get_template_file(results_dir,f"\/*-results-0.csv"),"r") as file:
        reader = csv.reader(file)
        results = {rows[0]: rows[-1] for rows in reader}
    results_dict = {k:[] for k in list(results.keys())}

    for file in os.listdir(results_dir):
        if file.split('-')[-2] == "results":
            with open(results_dir + f"/{file}", 'r') as results_file:
                reader = csv.reader(results_file)
                results = {rows[0]: rows[-1] for rows in reader}
                for key in results.keys():
                    if key != "name":
                        results_dict[key].extend([float(value) for value in results[key].split(",")])

    del results_dict['name']

    stats = defaultdict(list)
    for key,values in results_dict.items():
        if key != 'name' and len(values) > 1:
            stats[key].append(statistics.fmean(values))
            stats[key].append(statistics.median(values))
            stats[key].append(statistics.stdev(values))
            stats[key].append(statistics.variance(values))
            stats[key].append(min(values))
            stats[key].append(max(values))
            stats[key].append(np.quantile(values,[0,0.25,0.5,0.75,0.9,1]))
        else:
            stats[key].append(values[0])

    with open(analysis_file,'x', newline='') as analysis:
        csv_writer = csv.DictWriter(analysis, fieldnames=['name', 'mean', 'median', 'stdev', 'variance', 'min', 'max','quantiles', 'value'])
        csv_writer.writeheader()
        for name,values in stats.items():
            if len(values) > 1:
                csv_writer.writerow({'name': name,'mean': values[0], 'median': values[1], 'stdev': values[2], 'variance': values[3], 'min': values[4], 'max': values[5], 'quantiles': values[6]})
            else:
                csv_writer.writerow({'name': name, 'value': values[0]})


def convert_stats(hosts, results_dir, stats_path, output_dir):
    print(f"Logging stats to {stats_path}")
    host_names = [host.name for host in hosts]
    node_dirs = os.scandir(output_dir)
    stats = {}

    for node_dir in node_dirs:
        if node_dir.name in host_names:
            output_path = node_dir.path + f'/log/stats'
            with open(output_path, 'r') as output_file:
                while line := output_file.readline():
                    stat = line.split()
                    stats[stat[0]] = stat[1]

    with open(stats_path,'x', newline='') as stats_file:
        csv_writer = csv.DictWriter(stats_file, fieldnames=['name', 'size'])
        csv_writer.writeheader()
        for name,value in stats.items():
            csv_writer.writerow({'name': name,'size': value})


def analyse_stats(results_dir, analysis_file):
    with open(f"{results_dir}/" + get_template_file(results_dir,f"\/*-stats-0.csv"),"r") as file:
        reader = csv.reader(file)
        stats = {rows[0]: rows[-1] for rows in reader}
    stats_dict = {k:[] for k in list(stats.keys())}

    for file in os.listdir(results_dir):
        if file.split('-')[-2] == "stats":
            with open(results_dir + f"/{file}", 'r') as stats_file:
                reader = csv.reader(stats_file)
                stats = {rows[0]: rows[-1] for rows in reader}
                for key in stats.keys():
                    if key != "name":
                        stats_dict[key].extend([int(stats[key])])

    del stats_dict['name']

    stats = defaultdict(list)
    for key,values in stats_dict.items():
        if key != 'name' and len(values) > 1:
            stats[key].append(statistics.fmean(values))
            stats[key].append(statistics.median(values))
            stats[key].append(statistics.stdev(values))
            stats[key].append(statistics.variance(values))
        else:
            stats[key].append(values[0])

    with open(analysis_file,'a', newline='') as analysis:
        csv_writer = csv.DictWriter(analysis, fieldnames=['name', 'mean', 'median', 'stdev', 'variance', 'value'])
        csv_writer.writeheader()
        for name,values in stats.items():
            if len(values) > 1:
                csv_writer.writerow({'name': name,'mean': values[0], 'median': values[1], 'stdev': values[2], 'variance': values[3]})
            else:
                csv_writer.writerow({'name': name, 'value': values[0]})


def get_template_file(folder,pattern):
    files = os.listdir(folder)
    r = re.compile(pattern)
    files = [file for file in files if r.search(file)]
    return files[0]
