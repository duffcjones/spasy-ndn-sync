import os
import logging

from minindn.minindn import Minindn
from minindn.util import MiniNDNCLI
from minindn.apps.nfd import Nfd
from minindn.helpers.ndn_routing_helper import NdnRoutingHelper
from minindn.apps.app_manager import AppManager

from mininet.log import setLogLevel, info, error, debug

from mini.application.SpatialSyncApp import SpatialSyncApp
from mini.application.ConsumerApp import ConsumerApp
from mini.application.ProducerApp import ProducerApp

from mini.minindn_play.server import PlayServer
from mini.experiments.setup import Setup

logLevel = logging.WARN
setupDir = "/spatialsync/setup/"

globalPrefix = "/spasy/"
directPostfix = "/direct/"
multiPostfix = "/multi/"

initTime = 2
nFaces = 0

def run_experiment(topo_file):
    Setup.setup_dir = setupDir

    Setup.global_prefix = globalPrefix
    Setup.direct_postfix = directPostfix
    Setup.multi_postfix = multiPostfix

    Setup.log_level = logLevel
    Setup.init_time = initTime

    try:
        with os.scandir(Setup.setup_dir) as entries:
            for entry in entries:
                if entry.is_file():
                    os.unlink(entry.path)
        print("All files deleted successfully.")
    except OSError:
        print("Error occurred while deleting files.")

    setLogLevel("info")
    Minindn.cleanUp()
    Minindn.verifyDependencies()

    setups = {}

    ndn = Minindn(topoFile=topo_file)
    ndn.start()

    AppManager(ndn, ndn.net.hosts, Nfd)
    grh = NdnRoutingHelper(ndn.net)

    for i, host in enumerate(ndn.net.hosts):
        setup = Setup(host.name)
        node_prefix = setup.add_prefixes()
        setups[host.name] = setup
        grh.addOrigin([host], [node_prefix])

    grh.calculateNPossibleRoutes(nFaces=nFaces)

    for host in ndn.net.hosts:
        routesFromHost = host.cmd("nfdc route | grep -v '/localhost/nfd'")
        for dest in ndn.net.hosts:
            host_setup = setups[host.name]
            dest_setup = setups[dest.name]
            if dest_setup.node_prefix not in routesFromHost and dest.name != host.name:
                raise Exception("Route addition failed\n")
            if dest_setup.node_prefix in routesFromHost and dest.name != host.name:
                host_setup.add_route(dest_setup.node_prefix)

        info("Static route additions successful for node {}\n".format(host.name))

    for host in ndn.net.hosts:
        AppManager(ndn, [host], SpatialSyncApp,
                   config_file=setups[host.name].setup_config(),
                   actions_file=setups[host.name].setup_actions())

    # # MiniNDNCLI(ndn.net)
    PlayServer(ndn.net).start()
    ndn.stop()
