from mini.experiments.setup import Setup
from mini.experiments.experiment2 import run_experiments
from mini.experiments.util import make_topo

iterations = 1

topo_file_base = "/spatialsync/mini/experiments/scenario2/topologies/latency-{}.conf"
results_dir_base = "/spatialsync/mini/experiments/results/scenario2/latency-{}"
analysis_file = "analysis.csv"

packet_segment_size = 8800
waitTime = 1
num_nodes = 2
bandwidth = 1000
tree_size = 10
queue_size = 10
geocode = "dpwhwt"

if __name__ == "__main__":
    Setup.packet_segment_size = packet_segment_size
    Setup.wait_time = waitTime

    actions = [
        [f"INIT {geocode} {tree_size} {queue_size} 0", "ADD /add/data/dpwhwtsh401 0", "UPDATE 0"],
        [f"INIT {geocode} 0 1"]
    ]

    # latencies = [1,2,3,5,10]
    latencies = [1]
    for latency in latencies:
        topo = make_topo(num_nodes, latency, bandwidth)
        results_dir = results_dir_base.format(latency)
        run_experiments(topo, iterations, results_dir, analysis_file, actions)
