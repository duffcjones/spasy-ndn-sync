from collections import deque
from os import path, getcwd
import json
import logging
from typing import List


class Setup:
    """
    Class for initializing and holding configuration parameters for simulation nodes. Each node should have a setup instance associated with it by name.
    Configuration parameters and actions are output to separate files for each node in the defined setup folder.

    Attributes:
        base_path: Application prefix
        direct_root_hash_path: Base prefix for update interests by root hash
        direct_geocode_path: Base prefix for tree interests by geocode
        direct_asset_path: Base prefix for asset interests
        multi_path: Base prefix for multicast interests
        initialization_path: Base prefix for initialization interests

        setup_dir: Directory path that holds setup and action files
        output_dir: Directory path that holds output files from nodes
        packet_segment_size: Maximum packet segment size (bytes)
        packet_segment_size_overhead: Size overhead from packet signing (bytes)
        batch_size: Size of batches for requesting data segments
        log_level: Logging level for nodes (INFO = detailed logging, WARN = No logging)
        word_list_path: Path for word list to construct trees from
        request_asset: True if assets should be requested along with updates, False if not
        max_packets: Maximum number of segments to request for content
        build_tree_method: Method used to build trees. file = build a static tree from file, random = build a random tree with names from a list,
        use_timestamp: True if timestamps should be used when updating tree, False if not
        use_keychain_digest: True if NDN app should use dummy keychain for packet signing (improves performance), False if not.
                             If ndn-cxx was not patched during installation to use dummy keychain then dummy keychain must be used.
        action_list: List of action lists to distribute among nodes

        direct_root_hash_prefix: Prefix for update interests by root hash
        direct_geocode_prefix: Prefix for tree interests by geocode

        node_name: Name of node
        node_prefix: Base prefix for node
        multi_prefix: Prefix for receiving multicast interests
        initialization_prefix: Prefix for receiving initialization interests
        actions_file: Location of file containing actions for node
        config_file: Location of configuration file for node
        actions: List of actions for node
        multi_cast_routes: Prefixes for other nodes for multicast interests
        timer_output_path: File path for node timing results
        stats_output_path: File path for node statistics
    """

    base_path = "/spasy"
    direct_root_hash_path = "/direct/root"
    direct_geocode_path = "/direct/geocode"
    direct_asset_path = "/direct/asset"
    multi_path = "/multi"
    initialization_path = "/init"

    setup_dir = path.join(getcwd(),"setup")
    output_dir = "/tmp/minindn/"
    packet_segment_size = 8800
    packet_segment_size_overhead = 216
    batch_size = 0
    log_level = logging.INFO
    word_list_path = path.join(getcwd(), "resources", "spasy_tree.txt")
    request_asset = True
    max_packets = 100000
    build_tree_method = "file"
    use_timestamp = True
    use_keychain_digest = True
    action_list = deque()

    direct_root_hash_prefix = ""
    direct_geocode_prefix = ""


    def __init__(self, node_name: str) -> None:
        """
        Constructor for setup object (each node should have one setup object, associated by name).

        Args:
            node_name: Name of associated node
        """

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
        """
        Set naming prefixes shared by all nodes
        """

        cls.direct_root_hash_prefix = cls.base_path + cls.direct_root_hash_path
        cls.direct_geocode_prefix = cls.base_path + cls.direct_geocode_path
        cls.direct_asset_prefix = cls.base_path + cls.direct_asset_path


    @classmethod
    def add_actions(cls, actions: [[List[List[str]]]]) -> None:
        """
        Add node actions to simulation.

        Args:
            actions: List of node actions
        """

        for action in actions:
            cls.action_list.append(action)


    @classmethod
    def reset(cls) -> None:
        """
        Reset setup for new simulation
        """
        cls.action_list = deque()


    def add_prefixes(self):
        """
        Add name prefixes for a node.
        """

        self.node_prefix = self.base_path + f"/{self.node_name}"
        self.multi_prefix = self.node_prefix + self.multi_path
        self.initialization_prefix = self.node_prefix + self.initialization_path


    def add_route(self, node_prefix: str) -> None:
        """
        Add name prefixes for other nodes in the simulation (to allow for multicasting)

        Args:
            node_prefix: Name of other node
        """
        self.multi_cast_routes.append(node_prefix)


    def setup_actions(self) -> str:
        """
        Distribute actions to simulation nodes (stored in txt files).

        Returns:
            Txt file path with actions for node
        """

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
        """
        Write config information to file for nodes to use during simulation.

        Returns:
            Config file path for node
        """

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
