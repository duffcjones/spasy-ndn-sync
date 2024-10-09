from mini.experiments.setup import Setup
from mini.experiments.experiment2 import run_experiments
from mini.experiments.util import make_topo, clear_results

iterations = 10

topo_file_base = "/spatialsync/mini/experiments/scenario1/topologies/latency-{}.conf"
results_dir_base = "/spatialsync/mini/experiments/results/scenario1/treesize-{}"
analysis_file = "analysis.csv"

packet_segment_size = 8800
waitTime = 1
num_nodes = 2
bandwidth = 1000
latency = 2
queue_size = 10
geocode = "dpwhwt"

if __name__ == "__main__":
    Setup.packet_segment_size = packet_segment_size
    Setup.wait_time = waitTime

    tree_sizes = [10,100,1000,10000]
    # tree_sizes = [10]

    for tree_size in tree_sizes:
        clear_results("/tmp/minindn")
        topo = make_topo(num_nodes, latency, bandwidth)
        results_dir = results_dir_base.format(tree_size)
        actions = [
            [f"INIT {geocode} {tree_size} {queue_size} 0"],
            ["WAIT 20", f"JOIN {geocode} 0"]
        ]
        run_experiments(topo, iterations, results_dir, analysis_file, actions)
