from experiments.setup import Setup
from experiments.experiment import run_experiments
from experiments.util import make_topo, clear_results

results_dir = "scenario1/latency-{}"
experiment_name = "scenario1-latency-{}"

num_nodes = 3
num_mec_nodes = 1
bandwidth = 1000

tree_size = 1000
queue_size = 50
batch_size = 0
geocode = "dpwhwt"

experiment_wait_time = 25

if __name__ == "__main__":
    Setup.batch_size = batch_size

    actions = [
        ["SETUP 2", f"INIT {geocode} {tree_size} {queue_size} 0", f"SERVE_TREE {geocode} 0", "WAIT 5"],
        ["SETUP 2", f"INIT {geocode} {tree_size} {queue_size} 0", f"SERVE_TREE {geocode} 0", "WAIT 5"],
        ["SETUP 2",f"INIT {geocode} 1 1 15", f"JOIN {geocode} 0", "WAIT 5"]
    ]

    # latencies = [2,3,5,10,15]
    latencies = [2]

    for latency in latencies:
        topo = make_topo(num_nodes, num_mec_nodes, latency, bandwidth)
        run_experiments(topo, results_dir.format(latency), experiment_name.format(latency), actions, experiment_wait_time)
