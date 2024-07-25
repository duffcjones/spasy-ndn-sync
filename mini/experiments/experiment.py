import time

from minindn.minindn import Minindn
from minindn.util import MiniNDNCLI
from minindn.apps.nfd import Nfd
from minindn.helpers.ndn_routing_helper import NdnRoutingHelper
from minindn.apps.app_manager import AppManager

from mininet.log import setLogLevel, info, error, debug

from mini.application.SpatialSyncApp import SpatialSyncApp
from mini.application.ConsumerApp import ConsumerApp

logLevel = "info"
topoFile = "/spatialsync/mini/topologies/topology.conf"
globalNamePrefix = "/test/"

nFaces = 1

if __name__ == "__main__":
    setLogLevel(logLevel)
    Minindn.cleanUp()
    Minindn.verifyDependencies()

    ndn = Minindn(topoFile=topoFile)
    ndn.start()

    AppManager(ndn, ndn.net.hosts, Nfd)
    info("NFD started on nodes\n")
    time.sleep(5)

    grh = NdnRoutingHelper(ndn.net)
    for i, host in enumerate(ndn.net.hosts):
        grh.addOrigin([host], [globalNamePrefix + host.name])

    grh.calculateNPossibleRoutes(nFaces=nFaces)

    for host in ndn.net.hosts:
        routesFromHost = host.cmd("nfdc route | grep -v '/localhost/nfd'")
        debug(routesFromHost)
        for dest in ndn.net.hosts:
            if globalNamePrefix + dest.name not in routesFromHost and dest.name != host.name:
                raise Exception("Route addition failed\n")

        info("Static route additions successful for node {}\n".format(host.name))

    AppManager(ndn, [ndn.net.hosts[0]], SpatialSyncApp,
               source=globalNamePrefix + ndn.net.hosts[0].name,
               target=globalNamePrefix + ndn.net.hosts[2].name)
    AppManager(ndn, [ndn.net.hosts[2]], SpatialSyncApp,
               source=globalNamePrefix + ndn.net.hosts[2].name,
               target=globalNamePrefix + ndn.net.hosts[0].name)
    AppManager(ndn, [ndn.net.hosts[1]], ConsumerApp, target=globalNamePrefix + ndn.net.hosts[0].name)

    MiniNDNCLI(ndn.net)
    ndn.stop()
