import logging
import time

# logging.basicConfig(
#                     filemode='a',
#                     format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
#                     datefmt='%H:%M:%S',
#                     level=logging.INFO)


class Timer:
    def __init__(self):
        self.timers = {}
        self.start_time = None

    def start_timer(self, timer_name):
        # if self.start_time is not None:
        #     raise Exception("Timer already started")
        # else:
        #     self.start_time = time.perf_counter_ns()
        #     logging.debug(f"{self.start_time}")

        self.start_time = time.perf_counter_ns()

    def stop_timer(self, timer_name):
        # if self.start_time is None:
        #     raise Exception("Timer not started")
        # else:
        #     self.timers[timer_name] = time.perf_counter_ns() - self.start_time
        #     self.start_time = None
        #     # logging.debug(f"{self.timers[timer_name]}")
        elapsed_time = time.perf_counter_ns() - self.start_time
        self.timers[timer_name] = elapsed_time
        self.start_time = None

    def dump(self):
        logging.info(f'Dumping times {len(self.timers.items())}')
        for timer_name, timer_value in self.timers.items():
            logging.info(f'{timer_name}, {timer_value}, {timer_value // 1_000_000}')
