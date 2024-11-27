from experiments.setup import Setup
from experiments.experiment import run_experiments
from experiments.util import make_topo, clear_results

results_dir = "scenario2/treesize-{}"
experiment_file = "scenario2-treesize-{}"

num_nodes = 5
num_mec_nodes = 1
bandwidth = 1000
latency = 2

queue_size = 50
batch_size = 75
geocode = "dpwhwt"
request_asset = False

experiment_wait_time = 65

if __name__ == "__main__":
    Setup.batch_size = batch_size
    Setup.request_asset = request_asset

    tree_sizes = [10, 100, 1000, 10000, 50000]

    for tree_size in tree_sizes:
        topo = make_topo(num_nodes, num_mec_nodes, latency, bandwidth)
        actions = [
            ["SETUP 2", f"INIT {geocode} {tree_size} {queue_size} 5", "WAIT 30"],
            ["SETUP 2", f"INIT {geocode} {tree_size} {queue_size} 5", f"ADD /alice/ball/_v0/dpwhwtmpz0 0", "UPDATE 0", "WAIT 30"],
            ["SETUP 2", f"INIT {geocode} {tree_size} {queue_size} 5", "WAIT 30"]
        ]
        run_experiments(topo, results_dir.format(tree_size), experiment_file.format(tree_size), actions, experiment_wait_time)
