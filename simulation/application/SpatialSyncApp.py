from os import path, getcwd

from minindn.apps.application import Application
from mininet.log import info
from mininet.node import Host

# Build output folder
dist_folder = "../client/dist"

class SpatialSyncApp(Application):
    """
    Class for handling application initialization on simulation nodes.

    Attributes:
        log_file_name: Name of log file
        setup_file: Configuration file
        actions_file: Actions file
        cmd: Process to run on node
    """

    def __init__(self, node: Host, config_file: str, actions_file: str) -> None:
        """
        Class constructor for SpatialSyncApp class.

        Args:
            node: Mininet host
            config_file: Configuration file
            actions_file: Actions file
        """

        self.log_file_name = "log"
        self.setup_file = config_file
        self.actions_file = actions_file

        self.cmd = path.join(getcwd(), dist_folder, "SpatialSync")
        self.cmd += " " + config_file
        self.cmd += " --actions " + actions_file

        Application.__init__(self, node)

    def start(self) -> None:
        """
        Start defined process on node.
        """

        info("Starting spatial sync app on node {}\n".format(self.node.name))
        Application.start(self, self.cmd, self.log_file_name)
        return
