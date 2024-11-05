from mini.experiments.setup import Setup
from mini.experiments.experiment import run_experiments
from mini.experiments.util import make_topo, clear_results

topo_file_base = "/spatialsync/mini/experiments/scenario1/topologies/latency-{}.conf"
results_dir_base = "/spatialsync/mini/experiments/results/scenario1/latency-{}"
experiment_name = "scenario1-latency-{}"

packet_segment_size = 8800
batch_size = 0
waitTime = 1
num_nodes = 3
num_mec_nodes = 1
bandwidth = 1000
tree_size = 10000
queue_size = 50
geocode = "dpwhwt"
experimentWaitTime = 15

if __name__ == "__main__":
    Setup.packet_segment_size = packet_segment_size
    Setup.batch_size = batch_size
    Setup.wait_time = waitTime

    actions = [
        ["SETUP 2", f"INIT {geocode} {tree_size} {queue_size} 0", f"REGISTER_ROUTE {geocode}", "PREP_TREE 0", "WAIT 5"],
        ["SETUP 2", f"INIT {geocode} {tree_size} {queue_size} 0", f"REGISTER_ROUTE {geocode}", "PREP_TREE 0", "WAIT 5"],
        ["SETUP 2",f"INIT {geocode} 1 1 5", f"JOIN {geocode} 0", "WAIT 5"]
    ]

    latencies = [2,3,5,10,15]
    # latencies = [15]

    for latency in latencies:
        clear_results("/tmp/minindn")
        topo = make_topo(num_nodes, num_mec_nodes, latency, bandwidth)
        results_dir = results_dir_base.format(latency)
        run_experiments(topo, results_dir, experiment_name.format(latency), actions, experimentWaitTime)
