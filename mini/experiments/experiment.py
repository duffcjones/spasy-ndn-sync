import time
import os

from minindn.minindn import Minindn
from minindn.util import MiniNDNCLI
from minindn.apps.nfd import Nfd
from minindn.helpers.ndn_routing_helper import NdnRoutingHelper
from minindn.apps.app_manager import AppManager

from mininet.log import setLogLevel, info, error, debug

from mini.application.SpatialSyncApp import SpatialSyncApp
from mini.application.ConsumerApp import ConsumerApp
from mini.minindn_play.server import PlayServer
from mini.experiments.setup import Setup

logLevel = "info"
setupDir = "/spatialsync/setup/"
topoFile = "/spatialsync/mini/experiments/topologies/topology.conf"

globalPrefix = "/spasy/"
directPostfix = "/direct/"
multiPostfix = "/multi/"

root_geocode = "DPWHWT"
packet_segment_size = 1024
waitTime = 1

nFaces = 1

if __name__ == "__main__":
    setLogLevel(logLevel)
    Minindn.cleanUp()
    Minindn.verifyDependencies()

    try:
        with os.scandir(setupDir) as entries:
            for entry in entries:
                if entry.is_file():
                    os.unlink(entry.path)
        print("All files deleted successfully.")
    except OSError:
        print("Error occurred while deleting files.")

    Setup.setup_dir = setupDir

    Setup.global_prefix = globalPrefix
    Setup.direct_postfix = directPostfix
    Setup.multi_postfix = multiPostfix

    Setup.root_geocode = root_geocode
    Setup.packet_segment_size = packet_segment_size
    Setup.wait_time = waitTime

    setups = {}

    ndn = Minindn(topoFile=topoFile)
    ndn.start()

    AppManager(ndn, ndn.net.hosts, Nfd)
    info("NFD started on nodes\n")
    time.sleep(5)

    grh = NdnRoutingHelper(ndn.net)
    for i, host in enumerate(ndn.net.hosts):
        if host.name == "h0":
            setups[host.name] = Setup(host.name, "1")
        else:
            setups[host.name] = Setup(host.name, "2")
        grh.addOrigin([host], [globalPrefix + host.name])

    grh.calculateNPossibleRoutes(nFaces=nFaces)

    for host in ndn.net.hosts:
        routesFromHost = host.cmd("nfdc route | grep -v '/localhost/nfd'")
        debug(routesFromHost)
        for dest in ndn.net.hosts:
            if globalPrefix + dest.name not in routesFromHost and dest.name != host.name:
                raise Exception("Route addition failed\n")
            if globalPrefix + dest.name in routesFromHost and dest.name != host.name:
                setups[host.name].routes.append(globalPrefix + dest.name)

        info("Static route additions successful for node {}\n".format(host.name))

    AppManager(ndn, [ndn.net.hosts[0]], SpatialSyncApp,
               config_file=setups[ndn.net.hosts[0].name].setup_config(),
               actions_file=setups[ndn.net.hosts[0].name].setup_actions())
    AppManager(ndn, [ndn.net.hosts[1]], SpatialSyncApp,
               config_file=setups[ndn.net.hosts[1].name].setup_config(),
               actions_file=setups[ndn.net.hosts[1].name].setup_actions())
    AppManager(ndn, [ndn.net.hosts[2]], SpatialSyncApp,
               config_file=setups[ndn.net.hosts[2].name].setup_config(),
               actions_file=setups[ndn.net.hosts[2].name].setup_actions())
    AppManager(ndn, [ndn.net.hosts[3]], SpatialSyncApp,
               config_file=setups[ndn.net.hosts[3].name].setup_config(),
               actions_file=setups[ndn.net.hosts[3].name].setup_actions())
    AppManager(ndn, [ndn.net.hosts[4]], SpatialSyncApp,
               config_file=setups[ndn.net.hosts[4].name].setup_config(),
               actions_file=setups[ndn.net.hosts[4].name].setup_actions())
    # AppManager(ndn, [ndn.net.hosts[4]], ConsumerApp, target="/spasy/h0/direct/e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855")

    # MiniNDNCLI(ndn.net)
    PlayServer(ndn.net).start()
    ndn.stop()
