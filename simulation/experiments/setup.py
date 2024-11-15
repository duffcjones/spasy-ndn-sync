from collections import deque
from os import path, getcwd
import json
import logging
from typing import List


class Setup:
    base_path = "/spasy"
    direct_root_hash_path = "/direct/root"
    direct_geocode_path = "/direct/geocode"
    direct_asset_path = "/direct/asset"
    multi_path = "/multi"
    initialization_path = "/init"

    direct_root_hash_prefix = ""
    direct_gecode_prefix = ""

    setup_dir = path.join(getcwd(),"setup")
    output_dir = "/tmp/minindn/"
    packet_segment_size = 8800
    packet_segment_size_overhead = 216
    batch_size = 0
    log_level = logging.INFO
    init_time = 2
    word_list_path = path.join(getcwd(), "resources", "spasy_tree.txt")
    request_asset = True
    max_packets = 100000
    build_tree_method = "tree"
    use_timestamp = True
    use_keychain_digest = True

    action_list = deque()

    def __init__(self, node_name: str) -> None:
        self.node_name = node_name
        self.node_prefix = ""
        self.multi_prefix = ""
        self.initialization_prefix = ""

        self.actions_file = ""
        self.config_file = ""
        self.actions = []
        self.multi_cast_routes = []

        self.timer_output_path = path.join(self.output_dir, self.node_name, "log", "results")
        self.stats_output_path = path.join(self.output_dir, self.node_name, "log", "stats")

    @classmethod
    def init_global_prefixes(cls) -> None:
        cls.direct_root_hash_prefix = cls.base_path + cls.direct_root_hash_path
        cls.direct_geocode_prefix = cls.base_path + cls.direct_geocode_path
        cls.direct_asset_prefix = cls.base_path + cls.direct_asset_path

    @classmethod
    def add_actions(cls, actions: [[List[List[str]]]]) -> None:
        for action in actions:
            cls.action_list.append(action)

    @classmethod
    def reset(cls) -> None:
        cls.action_list = deque()

    def add_prefixes(self):
        self.node_prefix = self.base_path + f"/{self.node_name}"
        self.multi_prefix = self.node_prefix + self.multi_path
        self.initialization_prefix = self.node_prefix + self.initialization_path

    def add_route(self, node_prefix: str) -> None:
        self.multi_cast_routes.append(node_prefix)

    def setup_actions(self) -> str:
        if len(self.action_list) > 1:
            self.actions = self.action_list.popleft()
        else:
            self.actions = self.action_list[0]

        self.actions_file = path.join(self.setup_dir, f'{self.node_name}actions.txt')
        with open(self.actions_file, mode="w") as actions_file:
            for action in self.actions:
                actions_file.write(f"{action}\n")

        return self.actions_file

    def setup_config(self) -> str:
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
            "direct_asset_prefix": self.direct_asset_prefix,
            "base_path": self.base_path,
            "packet_segment_size": self.packet_segment_size - self.packet_segment_size_overhead,
            "batch_size": self.batch_size,
            "log_level": self.log_level,
            "init_time": self.init_time,
            "word_list_path": self.word_list_path,
            "request_asset": self.request_asset,
            "max_packets": self.max_packets,
            "build_tree_method": self.build_tree_method,
            "use_timestamp": self.use_timestamp,
            "use_keychain_digest": self.use_keychain_digest
        }

        self.config_file = path.join(self.setup_dir, f'{self.node_name}config.json')
        with open(self.config_file, mode="w") as setup_file:
            json.dump(setup_data, setup_file)
        return self.config_file
