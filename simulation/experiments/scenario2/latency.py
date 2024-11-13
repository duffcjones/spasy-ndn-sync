from experiments.setup import Setup
from experiments.experiment import run_experiments
from experiments.util import make_topo, clear_results

results_dir = "scenario2/latency-{}"
experiment_name = "scenario2-latency-{}"

num_nodes = 5
num_mec_nodes = 1
bandwidth = 1000

tree_size = 10000
queue_size = 50
batch_size = 100
geocode = "dpwhwt"
request_asset = False

experiment_wait_time = 15

if __name__ == "__main__":
    Setup.batch_size = batch_size
    Setup.request_asset = request_asset

    latencies = [2, 3, 5, 10, 15]

    actions = [
        ["SETUP 2", f"INIT {geocode} {tree_size} {queue_size} 5", "WAIT 5"],
        ["SETUP 2", f"INIT {geocode} {tree_size} {queue_size} 5", f"ADD /alice/ball/_v0/dpwhwtmpz0 0", "UPDATE 0", "WAIT 5"],
        ["SETUP 2", f"INIT {geocode} {tree_size} {queue_size} 5", "WAIT 5"]
    ]

    for latency in latencies:
        topo = make_topo(num_nodes, num_mec_nodes, latency, bandwidth)
        run_experiments(topo, results_dir.format(latency), experiment_name.format(latency), actions, experiment_wait_time)
