from collections import deque
from os.path import join
import json
import logging


class Setup:
    direct_postfix = "/direct/"
    multi_postfix = "/multi/"
    initialization_postfix = "/init/"
    global_prefix = "/spasy/"
    setup_dir = "/spatialsync/mini/experiments/setup/"
    root_geocode = "DPWHWT"
    packet_segment_size = 100
    log_level = logging.INFO
    wait_time = 1
    init_time = 2
    action_list = deque()

    def __init__(self, node_name):
        self.node_name = node_name
        self.direct_prefix = ""
        self.multi_prefix = ""
        self.initialization_prefix = ""
        self.node_prefix = ""

        self.actions_file = ""
        self.config_file = ""
        self.actions = []
        self.routes = []

    def add_prefixes(self):
        self.direct_prefix = self.global_prefix + self.node_name + self.direct_postfix
        self.multi_prefix = self.global_prefix + self.node_name + self.multi_postfix
        self.initialization_prefix = self.global_prefix + self.node_name + self.initialization_postfix
        self.node_prefix = self.global_prefix + self.node_name
        return self.node_prefix

    @classmethod
    def add_actions(cls, actions):
        cls.action_list.append(actions)

    def add_route(self, route):
        self.routes.append(route)

    def setup_config(self):
        setup_data = {
            "node_name": self.node_name,
            "direct_prefix": self.direct_prefix,
            "multi_prefix": self.multi_prefix,
            "initialization_prefix": self.initialization_prefix,
            "direct_postfix": self.direct_postfix,
            "multi_postfix": self.multi_postfix,
            "initialization_postfix": self.initialization_postfix,
            "routes": self.routes,
            "wait_time": self.wait_time,
            "packet_segment_size": self.packet_segment_size,
            "root_geocode": self.root_geocode,
            "log_level": self.log_level,
            "init_time": self.init_time
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
                actions_file.write(f"{action} {self.wait_time}\n")

        return self.actions_file
