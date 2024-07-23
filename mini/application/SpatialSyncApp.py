from minindn.apps.application import Application
from mininet.log import info


class SpatialSyncApp(Application):
    def __init__(self,node):
        Application.__init__(self, node)

    def start(self):
        info("Start spatial sync app on node {}\n".format(self.node.name))
        Application.start(self,"/spatialsync/client/dist/SpatialSync","spatialsync")
