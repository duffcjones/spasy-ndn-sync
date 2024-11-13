from experiments.setup import Setup
from experiments.experiment import run_experiments
from experiments.util import make_topo, clear_results

results_dir = "scenario2/treesize-{}"
experiment_file = "scenario2-treesize-{}"

packet_segment_size = 8800
batch_size = 75
waitTime = 1
num_nodes = 5
num_mec_nodes = 1
bandwidth = 1000
latency = 2
queue_size = 50
geocode = "dpwhwt"
request_asset = "False"
experimentWaitTime = 65

if __name__ == "__main__":
    Setup.packet_segment_size = packet_segment_size
    Setup.batch_size = batch_size
    Setup.wait_time = waitTime
    Setup.request_asset = request_asset

    tree_sizes = [10,100,1000,10000,50000]

    for tree_size in tree_sizes:
        topo = make_topo(num_nodes, num_mec_nodes, latency, bandwidth)
        actions = [
            ["SETUP 2", f"INIT {geocode} {tree_size} {queue_size} 5", "WAIT 30"],
            ["SETUP 2", f"INIT {geocode} {tree_size} {queue_size} 5", f"ADD /alice/ball/_v0/dpwhwtmpz0 0", "UPDATE 0", "WAIT 30"],
            ["SETUP 2", f"INIT {geocode} {tree_size} {queue_size} 5", "WAIT 30"]
        ]
        run_experiments(topo, results_dir.format(tree_size), experiment_file.format(tree_size), actions, experimentWaitTime)
