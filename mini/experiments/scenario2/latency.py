from mini.experiments.setup import Setup
from mini.experiments.experiment import run_experiments
from mini.experiments.util import make_topo, clear_results

topo_file_base = "/spatialsync/mini/experiments/scenario2/topologies/latency-{}.conf"
results_dir_base = "/spatialsync/mini/experiments/results/scenario2/latency-{}"
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

asset_path = "/spatialsync/mini/experiments/resources/baseball_01.bin"

if __name__ == "__main__":
    Setup.packet_segment_size = packet_segment_size
    Setup.batch_size = batch_size
    Setup.wait_time = waitTime
    Setup.request_asset = request_asset

    actions = [
        ["SETUP 2", f"INIT {geocode} {tree_size} {queue_size} 5", "WAIT 5"],
        ["SETUP 2", f"INIT {geocode} {tree_size} {queue_size} 5", "ADD /alice/ball/_v0/dpwhwtmpz0 {asset_path} 0", "UPDATE 0", "WAIT 5"],
        ["SETUP 2", f"INIT {geocode} {tree_size} {queue_size} 5", "WAIT 5"]
    ]

    # latencies = [2,3,5,10,15]
    latencies = [15]

    for latency in latencies:
        clear_results("/tmp/minindn")
        topo = make_topo(num_nodes, num_mec_nodes, latency, bandwidth)
        results_dir = results_dir_base.format(latency)
        # run_experiments(topo_file_base.format(latency), iterations, results_dir, experiment_name.format(latency), actions, experimentWaitTime)
        run_experiments(topo, results_dir, experiment_name.format(latency), actions, experimentWaitTime)