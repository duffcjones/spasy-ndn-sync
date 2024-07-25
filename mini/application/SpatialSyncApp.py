from minindn.apps.application import Application
from mininet.log import info


class SpatialSyncApp(Application):
    def __init__(self, node, source, target):
        self.cmd = "/spatialsync/client/dist/SpatialSync"
        self.cmd += " " + source
        self.cmd += " --target " + target

        self.logfileName = "log"
        self.source = source
        self.target = target

        Application.__init__(self, node)

    def start(self):
        info("Starting spatial sync app on node {} with prefix {}\n".format(self.node.name, self.source))
        Application.start(self, self.cmd, self.logfileName)
