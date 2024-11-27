from experiments.setup import Setup
from experiments.experiment import run_experiments
from experiments.util import make_topo, clear_results

results_dir = "scenario1/treesize-{}"
experiment_file = "scenario1-treesize-{}"

latency = 2
num_nodes = 3
num_mec_nodes = 1
bandwidth = 1000

queue_size = 50
batch_size = 100
geocode = "dpwhwt"

experiment_wait_time = 60

if __name__ == "__main__":
    Setup.batch_size = batch_size

    tree_sizes = [10, 100, 1000, 10000, 50000]

    for tree_size in tree_sizes:
        topo = make_topo(num_nodes, num_mec_nodes, latency, bandwidth)
        actions = [
            ["SETUP 2", f"INIT {geocode} {tree_size} {queue_size} 0", f"SERVE_TREE {geocode} 0", "WAIT 10"],
            ["SETUP 2", f"INIT {geocode} {tree_size} {queue_size} 0", f"SERVE_TREE {geocode} 0", "WAIT 10"],
            ["SETUP 2",f"INIT {geocode} 1 1 10", f"JOIN {geocode} 0", "WAIT 10"]
        ]

        run_experiments(topo, results_dir.format(tree_size), experiment_file.format(tree_size), actions, experiment_wait_time)
