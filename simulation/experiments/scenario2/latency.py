from experiments.setup import Setup
from experiments.experiment import run_experiments
from experiments.util import make_topo, clear_results

results_dir = "scenario2/latency-{}"
experiment_name = "scenario2-latency-{}"

packet_segment_size = 8800
batch_size = 100
waitTime = 5
num_nodes = 5
num_mec_nodes = 1
bandwidth = 1000
tree_size = 10000
queue_size = 50
geocode = "dpwhwt"
request_asset = "False"
experimentWaitTime = 15

if __name__ == "__main__":
    Setup.packet_segment_size = packet_segment_size
    Setup.batch_size = batch_size
    Setup.wait_time = waitTime
    Setup.request_asset = request_asset

    actions = [
        ["SETUP 2", f"INIT {geocode} {tree_size} {queue_size} 5", "WAIT 5"],
        ["SETUP 2", f"INIT {geocode} {tree_size} {queue_size} 5", f"ADD /alice/ball/_v0/dpwhwtmpz0 0", "UPDATE 0", "WAIT 5"],
        ["SETUP 2", f"INIT {geocode} {tree_size} {queue_size} 5", "WAIT 5"]
    ]

    latencies = [2,3,5,10,15]

    for latency in latencies:
        topo = make_topo(num_nodes, num_mec_nodes, latency, bandwidth)
        run_experiments(topo, results_dir.format(latency), experiment_name.format(latency), actions, experimentWaitTime)
