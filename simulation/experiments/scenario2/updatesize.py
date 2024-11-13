from experiments.setup import Setup
from experiments.experiment import run_experiments
from experiments.util import make_topo, clear_results

results_dir_base = "scenario2/updatesize-{}"
experiment_file = "scenario2-updatesize-{}"

packet_segment_size = 8800
batch_size = 100
waitTime = 1
num_nodes = 5
num_mec_nodes = 1
bandwidth = 1000
latency = 2
tree_size = 10000
geocode = "dpwhwt"
request_asset = "False"
experimentWaitTime = 15


if __name__ == "__main__":
    Setup.packet_segment_size = packet_segment_size
    Setup.batch_size = batch_size
    Setup.wait_time = waitTime
    Setup.request_asset = request_asset

    queue_sizes = [10,25,50,100,250]

    for queue_size in queue_sizes:
        topo = make_topo(num_nodes, num_mec_nodes, latency, bandwidth)
        actions = [
            ["SETUP 2", f"INIT {geocode} {tree_size} {queue_size} 5", "WAIT 5"],
            ["SETUP 2", f"INIT {geocode} {tree_size} {queue_size} 5", f"ADD /alice/ball/_v0/dpwhwtmpz0 0", "UPDATE 0", "WAIT 5"],
            ["SETUP 2", f"INIT {geocode} {tree_size} {queue_size} 5", "WAIT 5"]
        ]
        run_experiments(topo, results_dir.format(queue_size), experiment_file.format(queue_size), actions, experimentWaitTime)
