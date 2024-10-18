import logging
import time
from collections import defaultdict
import Config


class Timer:
    def __init__(self, output_path):
        self.timers = defaultdict(list)
        self.output_path = output_path
        self.log_name = Config.config["node_name"] + "_{}"

    def start_timer(self, timer_name):
        self.timers[self.log_name.format(timer_name)] = [time.perf_counter_ns()]

    def stop_timer(self, timer_name):
        if len(self.timers[self.log_name.format(timer_name)]) < 1:
            self.timers[self.log_name.format(timer_name)].append("none")
        self.timers[self.log_name.format(timer_name)].append(time.perf_counter_ns())

    def start_global_timer(self, timer_name):
        self.timers[timer_name] = [time.perf_counter_ns()]

    def stop_global_timer(self, timer_name):
        if len(self.timers[timer_name]) < 1:
            self.timers[timer_name].append("none")
        self.timers[timer_name].append(time.perf_counter_ns())


    def dump(self):
        logging.info(f'Dumping {len(self.timers.items())} times to {self.output_path}')

        with open(self.output_path, 'w') as results_file:
            for timer_name, timer_values in self.timers.items():
                result = f'{timer_name} '
                for value in timer_values:
                    result += f'{value} '
                results_file.write(result + "\n")
