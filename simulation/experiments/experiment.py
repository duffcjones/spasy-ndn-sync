from os import path, unlink, getcwd, makedirs, scandir
import logging
from time import sleep
from datetime import datetime
from argparse import ArgumentParser

from minindn.minindn import Minindn
from minindn.util import MiniNDNCLI
from minindn.apps.nfd import Nfd
from minindn.helpers.nfdc import Nfdc
from minindn.helpers.ndn_routing_helper import NdnRoutingHelper
from minindn.apps.app_manager import AppManager

from mininet.log import setLogLevel, info, error, debug

from application.SpatialSyncApp import SpatialSyncApp
from minindn_play.server import PlayServer
from experiments.setup import Setup
from experiments.results import convert_results, convert_stats, analyse_stats, analyse_results
from experiments.util import clear_results

nfaces = 1
minindn_path = "/tmp/minindn"
results_root_dir = "results"


def run_experiments(topo, results_dir, experiment_name, actions, time_to_wait):
    parser = ArgumentParser()
    parser.add_argument('iterations')
    parser.add_argument('-c', '--cli', action='store_true', dest='use_cli')
    parser.add_argument('-g', '--gui', action='store_true', dest='use_gui')
    parser.add_argument('-i', '--info', action='store_true', dest='log_info')
    parser.add_argument('-t', '--topo', dest='topo_file')
    args = parser.parse_args()

    clear_results(minindn_path)
    results_dir_path = path.join(getcwd(), results_root_dir, results_dir, datetime.now().strftime('%d-%m-%Y-%H-%M-%S'))
    makedirs(results_dir_path, exist_ok=True)
    print(f"Logging experiments to {results_dir_path}")

    if args.log_info:
        print("Logging enabled")
        Setup.log_level = logging.INFO
    else:
        print("Logging disabled")
        Setup.log_level = logging.WARN

    print(f"Running {args.iterations} iterations")
    for i in range(int(args.iterations)):
        results_path = path.join(results_dir_path, f"{experiment_name}-results-{i}.csv")
        stats_path = path.join(results_dir_path, f"{experiment_name}-stats-{i}.csv")
        print(f"Running experiment iteration {i}")
        run_experiment(topo, results_dir_path, results_path, stats_path, actions, time_to_wait, parser, args)

    analysis_path = path.join(results_dir_path, f"{experiment_name}-analysis.csv")
    print(f"Outputting analysis to {analysis_path}")
    analyse_results(results_dir_path, analysis_path)
    analyse_stats(results_dir_path, analysis_path)


def run_experiment(topo, results_dir, results_path, stats_path, actions, time_to_wait, parser, args):
    Setup.init_global_prefixes()
    Setup.add_actions(actions)

    try:
        with scandir(Setup.setup_dir) as entries:
            for entry in entries:
                if entry.is_file():
                    unlink(entry.path)
        print("All files deleted successfully")
    except OSError:
        print("Error occurred while deleting setup files")

    setLogLevel("info")
    Minindn.cleanUp()
    Minindn.verifyDependencies()

    if args.topo_file:
        ndn = Minindn(parser, topoFile=args.topofile)
    else:
        ndn = Minindn(parser, topo=topo)
    ndn.start()

    AppManager(ndn, ndn.net.hosts, Nfd)
    sleep(2)

    grh = NdnRoutingHelper(ndn.net)
    setups = {}
    for host in ndn.net.hosts:
        setup = Setup(host.name)
        setup.add_prefixes()
        setups[host.name] = setup
        grh.addOrigin([host], [Setup.base_path])
        grh.addOrigin([host], [setup.node_prefix])
    grh.calculateNPossibleRoutes(nFaces=nfaces)

    for host in ndn.net.hosts:
        # routesFromHost = host.cmd("nfdc route | grep -v '/localhost/nfd'")
        for dest in ndn.net.hosts:
            host_setup = setups[host.name]
            dest_setup = setups[dest.name]
            if dest.name != host.name:
                host_setup.add_route(dest_setup.node_prefix)
        info(f"List of nodes added for node {host.name}\n")

    for host in ndn.net.hosts:
        AppManager(ndn, [host], SpatialSyncApp,
                   config_file=setups[host.name].setup_config(),
                   actions_file=setups[host.name].setup_actions())
    sleep(time_to_wait)

    # Use either CLI or NDN Play (NDN Play won't work on vm if you can't port forward 8008 and 8765)
    if args.use_gui:
        PlayServer(ndn.net).start()
    elif args.use_cli:
        MiniNDNCLI(ndn.net)
    ndn.stop()

    convert_results(ndn.net.hosts, results_dir, results_path, Setup.output_dir)
    convert_stats(ndn.net.hosts, results_dir, stats_path, Setup.output_dir)
    Setup.reset()
