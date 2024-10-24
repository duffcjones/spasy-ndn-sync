from mini.experiments.setup import Setup
from mini.experiments.experiment import run_experiments
from mini.experiments.util import make_topo, clear_results

iterations = 1

topo_file_base = "/spatialsync/mini/experiments/scenario1/topologies/latency-{}.conf"
results_dir_base = "/spatialsync/mini/experiments/results/scenario1/queuesize-{}"
analysis_file = "analysis.csv"

packet_segment_size = 8800
waitTime = 1
num_nodes = 3
bandwidth = 1000
latency = 2
tree_size = 10000
geocode = "dpwhwt"
experimentWaitTime = 15

if __name__ == "__main__":
    Setup.packet_segment_size = packet_segment_size
    Setup.wait_time = waitTime

    # queue_sizes = [10,25,50,100,1000]
    queue_sizes = [500]

    for queue_size in queue_sizes:
        topo = make_topo(num_nodes, latency, bandwidth)
        results_dir = results_dir_base.format(queue_size)
        actions = [
            ["SETUP 2",f"INIT {geocode} 1 1 5", "WAIT 5"]
            ["SETUP 2", f"INIT {geocode} {tree_size} {queue_size} 0", "PREP_TREE 0", "WAIT 5"],
            ["SETUP 2",f"INIT {geocode} 1 1 5", f"JOIN {geocode} 0", "WAIT 5"]
        ]

        run_experiments(topo, iterations, results_dir, analysis_file, actions, experimentWaitTime)
