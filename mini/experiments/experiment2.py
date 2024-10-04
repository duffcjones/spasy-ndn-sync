import os
import logging
import time
from datetime import datetime

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
from mini.experiments.results import convert_results
from mini.experiments.results import analyse_results

log_level = logging.INFO
setup_dir = "/spatialsync/setup/"
output_dir = "/tmp/minindn/"

init_time = 2
nFaces = 0

base_path = "/spasy"
direct_root_hash_path = "/direct/root"
direct_geocode_path = "/direct/geocode"
multi_path = "/multi"
initialization_path = "/init"


def run_experiments(topo_file, iterations, results_dir, analysis_file):
    # results_dir = results_dir + f"/{datetime.now().strftime('%d-%m-%Y-%H-%M-%S')}"
    results_dir = results_dir + "/04-10-2024-01-43-14"

    os.makedirs(results_dir, exist_ok=True)
    print(f"Logging experiments to {results_dir}")
    for i in range(iterations):
        results_path = results_dir + f"/results{i}.csv"
        print(f"Running experiment iteration {i}")
        print(Setup.action_list)
        run_experiment(topo_file, results_dir, results_path)

    analysis_path = results_dir + f"/{analysis_file}"
    print(f"Running analysis file {analysis_path}")
    analyse_results(results_dir, analysis_path)



def run_experiment(topo_file, results_dir, results_path):
    # Setup.setup_dir = setup_dir
    # Setup.log_level = log_level
    # Setup.output_dir = output_dir
    # Setup.init_time = init_time
    #
    # Setup.base_path = base_path
    # Setup.direct_root_hash_path = direct_root_hash_path
    # Setup.direct_geocode_path = direct_geocode_path
    # Setup.multi_path = multi_path
    # Setup.initialization_path = initialization_path
    #
    # Setup.init_global_prefixes()
    #
    # try:
    #     with os.scandir(Setup.setup_dir) as entries:
    #         for entry in entries:
    #             if entry.is_file():
    #                 os.unlink(entry.path)
    #     print("All files deleted successfully.")
    # except OSError:
    #     print("Error occurred while deleting files.")
    #
    # setLogLevel("info")
    # Minindn.cleanUp()
    # Minindn.verifyDependencies()
    #
    # setups = {}
    #
    ndn = Minindn(topoFile=topo_file)
    ndn.start()
    #
    # AppManager(ndn, ndn.net.hosts, Nfd)
    # grh = NdnRoutingHelper(ndn.net)
    #
    # for i, host in enumerate(ndn.net.hosts):
    #     setup = Setup(host.name)
    #     setup.add_prefixes()
    #     setups[host.name] = setup
    #     grh.addOrigin([host], [Setup.base_path])
    #     grh.addOrigin([host], [setup.node_prefix])
    #
    # grh.calculateNPossibleRoutes(nFaces=nFaces)
    #
    # for host in ndn.net.hosts:
    #     # routesFromHost = host.cmd("nfdc route | grep -v '/localhost/nfd'")
    #     for dest in ndn.net.hosts:
    #         host_setup = setups[host.name]
    #         dest_setup = setups[dest.name]
    #         if dest.name != host.name:
    #             host_setup.add_route(dest_setup.node_prefix)
    #     info("Static route additions successful for node {}\n".format(host.name))
    #
    # for host in ndn.net.hosts:
    #     AppManager(ndn, [host], SpatialSyncApp,
    #                config_file=setups[host.name].setup_config(),
    #                actions_file=setups[host.name].setup_actions())
    #
    # time.sleep(9)
    #
    # # MiniNDNCLI(ndn.net)
    # PlayServer(ndn.net).start()
    #
    ndn.stop()

    convert_results(ndn.net.hosts, results_dir, results_path, output_dir)
    Setup.reset()
