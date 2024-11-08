from minindn.apps.application import Application
from mininet.log import info


class SpatialSyncApp(Application):
    def __init__(self, node, config_file, actions_file):
        self.logfileName = "log"
        self.setup_file = config_file
        self.actions_file = actions_file

        self.cmd = "/spatialsync/client/dist/SpatialSync"
        self.cmd += " " + config_file
        self.cmd += " --actions " + actions_file

        Application.__init__(self, node)

    def start(self):
        info("Starting spatial sync app on node {}\n".format(self.node.name))
        Application.start(self, self.cmd, self.logfileName)
