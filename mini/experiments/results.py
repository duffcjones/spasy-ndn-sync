import os
import csv
from collections import defaultdict
import statistics


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
            csv_writer.writerow({'name': name,'start': values[0],'end': values[1:],'time': ",".join([str(round((int(i) - int(values[0])) / 1000000)) for i in values[1:]])})


def analyse_results(results_dir, analysis_file):
    with open(results_dir + f"/{os.listdir(results_dir)[0]}","r") as file:
        reader = csv.reader(file)
        results = {rows[0]: rows[-1] for rows in reader}
    results_dict = {k:[] for k in list(results.keys())}

    for file in os.listdir(results_dir):
        with open(results_dir + f"/{file}", 'r') as results_file:
            reader = csv.reader(results_file)
            results = {rows[0]: rows[-1] for rows in reader}
            for key in results.keys():
                if key != "name":
                    results_dict[key].extend([int(value) for value in results[key].split(",")])

    del results_dict['name']

    stats = defaultdict(list)
    for key,values in results_dict.items():
        if key != 'name' and len(values) > 1:
            stats[key].append(statistics.fmean(values))
            stats[key].append(statistics.median(values))
            stats[key].append(statistics.stdev(values))
            stats[key].append(statistics.variance(values))
        else:
            stats[key].append(values[0])

    with open(analysis_file,'x', newline='') as analysis:
        csv_writer = csv.DictWriter(analysis, fieldnames=['name', 'mean', 'median', 'stdev', 'variance', 'value'])
        csv_writer.writeheader()
        for name,values in stats.items():
            if len(values) > 1:
                csv_writer.writerow({'name': name,'mean': values[0], 'median': values[1], 'stdev': values[2], 'variance': values[3]})
            else:
                csv_writer.writerow({'name': name, 'value': values[0]})
