import time

from minindn.minindn import Minindn
from minindn.util import MiniNDNCLI
from minindn.apps.app_manager import AppManager
from minindn.apps.nfd import Nfd
from minindn.helpers.ndn_routing_helper import NdnRoutingHelper
from minindn.apps.app_manager import AppManager
from minindn.apps.application import Application

from mininet.log import setLogLevel, info, error
from mini.application.SpatialSyncApp import SpatialSyncApp

if __name__ == '__main__':
    # mini general setup
    setLogLevel('info')
    Minindn.cleanUp()
    Minindn.verifyDependencies()

    ndn = Minindn(topoFile='/spatialsync/mini/topologies/topology.conf')
    ndn.start()

    info('Starting NFD on nodes\n')
    nfds = AppManager(ndn, ndn.net.hosts, Nfd)
    time.sleep(5)

    info('Adding static routes to NFD\n')
    grh = NdnRoutingHelper(ndn.net)
    grh.addOrigin([ndn.net['h1']], ["/example/1"])
    grh.addOrigin([ndn.net['h2']], ["/example/2"])
    grh.addOrigin([ndn.net['h3']], ["/example/3"])
    grh.addOrigin([ndn.net['h4']], ["/example/4"])
    grh.addOrigin([ndn.net['h5']], ["/example/5"])

    grh.calculateNPossibleRoutes(nFaces=1)
    routesFromh1 = ndn.net['h1'].cmd("nfdc route | grep -v '/localhost/nfd'")
    info(routesFromh1)
    if '/ndn/h2-site/h2' not in routesFromh1:
        info('Route addition failed\n')
    else:
        info('Route addition successful\n')

    AppManager(ndn, [ndn.net['h1']], SpatialSyncApp)

    MiniNDNCLI(ndn.net)
    ndn.stop()
