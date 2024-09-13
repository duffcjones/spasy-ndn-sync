from os.path import join
import json


class Setup():
    direct_postfix = "/direct/"
    multi_postfix = "/multi/"
    initialization_postfix = "/init/"
    global_prefix = "/spasy/"
    setup_dir = "/spatialsync/mini/experiments/setup/"
    root_geocode = "DPWHWT"
    packet_segment_size = 100
    wait_time = 1
    action_list = {
        "1": ["WAIT", "UPDATE"],
        "2": ["WAIT", "WAIT"]
    }

    def __init__(self, node_name, actions):
        self.node_name = node_name
        self.direct_prefix = self.global_prefix + node_name + self.direct_postfix
        self.multi_prefix = self.global_prefix + node_name + self.multi_postfix
        self.initialization_prefix = self.global_prefix + node_name + self.initialization_postfix
        self.actions_file = join(self.setup_dir, f'{self.node_name}actions.txt')
        self.config_file = join(self.setup_dir, f'{self.node_name}config.json')
        self.actions = self.action_list[actions]
        self.routes = []

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
        }

        with open(self.config_file, mode="w", encoding="utf-8") as setup_file:
            json.dump(setup_data, setup_file)

        return self.config_file

    def setup_actions(self):
        with open(self.actions_file, mode="w", encoding="utf-8") as actions_file:
            for action in self.actions:
                actions_file.write(f"{action} {self.wait_time}\n")

        return self.actions_file
