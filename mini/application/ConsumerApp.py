from minindn.apps.application import Application
from mininet.log import info


class ConsumerApp(Application):
    def __init__(self, node, target):
        self.cmd = "/spatialsync/client/dist/Consumer"
        self.cmd += " " + target

        self.logfileName = "log"

        Application.__init__(self, node)

    def start(self):
        info("Starting consumer app on node {}\n".format(self.node.name))
        Application.start(self, self.cmd, self.logfileName)
