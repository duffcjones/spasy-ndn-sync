from os import path, getcwd

from experiments.setup import Setup
from experiments.experiment import run_experiments
from experiments.util import make_topo, clear_results

results_dir = "scenario3/treesize-{}"
experiment_file = "scenario3-treesize-{}"

num_nodes = 2
num_mec_nodes = 1
bandwidth = 1000
latency = 2

queue_size = 50
batch_size = 75
geocode = "dpwhwt"
request_asset = True
asset_path = path.join(getcwd(), "resources/beach_ball.glb")

experiment_wait_time = 65

if __name__ == "__main__":
    Setup.batch_size = batch_size
    Setup.request_asset = request_asset

    tree_sizes = [100, 1000, 5000, 10000, 15000, 20000, 25000]

    for tree_size in tree_sizes:
        topo = make_topo(num_nodes, num_mec_nodes, latency, bandwidth)

        actions = [
            ["SETUP 2", f"INIT {geocode} {tree_size} {queue_size} 5", "WAIT 30"],
            ["SETUP 2", f"INIT {geocode} {tree_size} {queue_size} 5", f"ADD /alice/ball/_v0/dpwhwtmpz0 {asset_path} 0", "WAIT 30"],
            ["SETUP 2", f"INIT {geocode} {tree_size} {queue_size} 5", "WAIT 30"]
        ]

        run_experiments(topo, results_dir.format(tree_size), experiment_file.format(tree_size), actions, experiment_wait_time)
