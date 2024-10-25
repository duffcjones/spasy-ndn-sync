from collections import deque
from os.path import join
import json
import logging


class Setup:
    base_path = "/spasy"
    direct_root_hash_path = "/direct/root"
    direct_geocode_path = "/direct/geocode"
    multi_path = "/multi"
    initialization_path = "/init"

    direct_root_hash_prefix = ""
    direct_gecode_prefix = ""

    setup_dir = "/spatialsync/mini/experiments/setup/"
    output_dir = "/tmp/minindn/"
    packet_segment_size = 8800
    packet_segment_size_overhead = 128 + 88
    log_level = logging.INFO
    wait_time = 1
    init_time = 2
    word_list_path = "/spatialsync/mini/experiments/spasy_tree.txt"

    action_list = deque()

    def __init__(self, node_name):
        self.node_name = node_name
        self.node_prefix = ""
        self.multi_prefix = ""
        self.initialization_prefix = ""

        self.actions_file = ""
        self.config_file = ""
        self.actions = []
        self.multi_cast_routes = []

        self.timer_output_path = self.output_dir + f"{self.node_name}/log/results"
        self.stats_output_path = self.output_dir + f"{self.node_name}/log/stats"

    @classmethod
    def init_global_prefixes(cls):
        cls.direct_root_hash_prefix = cls.base_path + cls.direct_root_hash_path
        cls.direct_geocode_prefix = cls.base_path + cls.direct_geocode_path

    def add_prefixes(self):
        self.node_prefix = self.base_path + f"/{self.node_name}"
        self.multi_prefix = self.node_prefix + self.multi_path
        self.initialization_prefix = self.node_prefix + self.initialization_path

    @classmethod
    def add_actions(cls, actions):
        cls.action_list.append(actions)

    def add_route(self, node_prefix):
        self.multi_cast_routes.append(node_prefix)

    def setup_config(self):
        setup_data = {
            "node_name": self.node_name,
            "timer_output_path": self.timer_output_path,
            "stats_output_path": self.stats_output_path,
            "direct_root_hash_prefix": self.direct_root_hash_prefix,
            "direct_geocode_prefix": self.direct_geocode_prefix,
            "multi_prefix": self.multi_prefix,
            "initialization_prefix": self.initialization_prefix,
            "multi_cast_routes": self.multi_cast_routes,
            "multi_path": self.multi_path,
            "initialization_path": self.initialization_path,
            "direct_root_hash_path": self.direct_root_hash_path,
            "direct_geocode_path": self.direct_geocode_path,
            "base_path": self.base_path,
            "wait_time": self.wait_time,
            "packet_segment_size": self.packet_segment_size - self.packet_segment_size_overhead,
            "log_level": self.log_level,
            "init_time": self.init_time,
            "word_list_path": self.word_list_path
        }
        self.config_file = join(self.setup_dir, f'{self.node_name}config.json')
        with open(self.config_file, mode="w") as setup_file:
            json.dump(setup_data, setup_file)
        return self.config_file

    def setup_actions(self):
        if len(self.action_list) > 1:
            self.actions = self.action_list.popleft()
        else:
            self.actions = self.action_list[0]

        self.actions_file = join(self.setup_dir, f'{self.node_name}actions.txt')
        with open(self.actions_file, mode="w") as actions_file:
            for action in self.actions:
                actions_file.write(f"{action}\n")

        return self.actions_file

    @classmethod
    def reset(cls):
        cls.action_list = deque()
