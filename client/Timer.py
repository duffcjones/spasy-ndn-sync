import logging
import time
import Config
from collections import defaultdict


class Timer:
    """
    Class for keeping timing results. Keeps timers that mark start and end times. Timers can be started and stopped on different
    nodes as long as timer names are kept consistent. Times are recorded to txt file to be processed after simulation.
    """

    def __init__(self, output_path: str) -> None:
        """
        Constructor for Timer class

        Args:
            output_path: Path to output times to
        """

        self.timers = defaultdict(list)
        self.output_path = output_path
        self.log_name = Config.config["node_name"] + "_{}"

    def start_timer(self, timer_name: str) -> None:
        """
        Start a timer (can only be used if the timer is stopped on this node) at current time. Times are recorded to nanosecond precision.

        Args:
            timer_name: Name of timer
        """
        self.timers[self.log_name.format(timer_name)] = [time.perf_counter_ns()]

    def stop_timer(self, timer_name: str) -> None:
        """
        Stop a timer (can only be used if the timer was started on this node) at current time. Times are recorded to nanosecond precision.

        Args:
            timer_name: Name of timer
        """

        if len(self.timers[self.log_name.format(timer_name)]) < 1:
            self.timers[self.log_name.format(timer_name)].append("none")
        self.timers[self.log_name.format(timer_name)].append(time.perf_counter_ns())

    def start_global_timer(self, timer_name: str) -> None:
        """
        Start a timer (can only be used if the timer is stopped on another node) at current time. Times are recorded to nanosecond precision.

        Args:
            timer_name: Name of timer (needs to be consistent with name of timer used when being stopped on another node)
        """

        self.timers[timer_name] = [time.perf_counter_ns()]

    def stop_global_timer(self, timer_name: str) -> None:
        """
        Stop a timer (can only be used if the timer was started on another node) at current time. Times are recorded to nanosecond precision.

        Args:
            timer_name: Name of timer (needs to be consistent with name of timer used when started on another node)
        """

        if len(self.timers[timer_name]) < 1:
            self.timers[timer_name].append("none")
        self.timers[timer_name].append(time.perf_counter_ns())


    def dump(self) -> None:
        """
         Dump times to file
        """

        logging.info(f'Dumping {len(self.timers.items())} times to {self.output_path}')

        with open(self.output_path, 'w') as results_file:
            for timer_name, timer_values in self.timers.items():
                result = f'{timer_name} '
                for value in timer_values:
                    result += f'{value} '
                results_file.write(result + "\n")
