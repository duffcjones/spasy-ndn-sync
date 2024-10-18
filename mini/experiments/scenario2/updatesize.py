from mini.experiments.scenario2.latency import queue_size
from mini.experiments.setup import Setup
from mini.experiments.experiment2 import run_experiments
from mini.experiments.util import make_topo, clear_results

iterations = 10

topo_file_base = "/spatialsync/mini/experiments/scenario2/topologies/latency-{}.conf"
results_dir_base = "/spatialsync/mini/experiments/results/scenario2/queuesize-{}"
analysis_file = "analysis.csv"

packet_segment_size = 8800
waitTime = 1
num_nodes = 5
bandwidth = 1000
latency = 2
tree_size = 1000
geocode = "dpwhwt"

if __name__ == "__main__":
    Setup.packet_segment_size = packet_segment_size
    Setup.wait_time = waitTime

    # queue_sizes = [10,25,50,100,1000]
    queue_sizes = [1000]

    for queue_size in queue_sizes:
        topo = make_topo(num_nodes, latency, bandwidth)
        results_dir = results_dir_base.format(queue_size)
        actions = [
            [f"INIT {geocode} {queue_size} {queue_size} 0", "ADD /add/data/dpwhwtsh401 0", "UPDATE 0"],
            [f"INIT {geocode} 1 1 5", "WAIT 2"]
        ]
        run_experiments(topo, iterations, results_dir, analysis_file, actions)
