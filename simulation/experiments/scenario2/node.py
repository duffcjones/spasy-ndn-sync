from experiments.setup import Setup
from experiments.experiment import run_experiments
from experiments.util import make_topo, clear_results

results_dir = "scenario2/nodes-{}"
experiment_name = "scenario2-node-{}"

bandwidth = 1000
latency = 2

tree_size = 10000
queue_size = 50
batch_size = 100
geocode = "dpwhwt"
request_asset = False

experiment_wait_time = 15

if __name__ == "__main__":
    Setup.batch_size = batch_size
    Setup.request_asset = request_asset

    num_nodes = [3, 5, 10, 15, 19]
    num_mec_nodes = 1

    for num_node in num_nodes:
        topo = make_topo(num_node, num_mec_nodes, latency, bandwidth)
        actions = [
            ["SETUP 2", f"INIT {geocode} {tree_size} {queue_size} 5", "WAIT 5"],
            ["SETUP 2", f"INIT {geocode} {tree_size} {queue_size} 5", f"ADD /alice/ball/_v0/dpwhwtmpz0 0", "UPDATE 0", "WAIT 5"],
            ["SETUP 2", f"INIT {geocode} {tree_size} {queue_size} 5", "WAIT 5"]
        ]
        run_experiments(topo, results_dir.format(num_node), experiment_name.format(num_node), actions, experiment_wait_time)
