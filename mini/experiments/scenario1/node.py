from mini.experiments.setup import Setup
from mini.experiments.experiment2 import run_experiments
from mini.experiments.util import make_topo, clear_results

iterations = 10

topo_file_base = "/spatialsync/mini/experiments/scenario1/topologies/nodes-{}.conf"
results_dir_base = "/spatialsync/mini/experiments/results/scenario1/nodes-{}"
analysis_file = "analysis.csv"

packet_segment_size = 8800
waitTime = 1
num_nodes = 2
bandwidth = 1000
latency = 2
tree_size = 100
queue_size = 10
geocode = "dpwhwt"

if __name__ == "__main__":
    Setup.packet_segment_size = packet_segment_size
    Setup.wait_time = waitTime

    # num_nodes = [5, 10, 15, 20]
    num_nodes = [20]

    for num_node in num_nodes:
        clear_results("/tmp/minindn")
        topo = make_topo(num_node, latency, bandwidth)
        results_dir = results_dir_base.format(num_node)
        actions = [
            [f"INIT {geocode} {tree_size} {queue_size} 0"],
            ["WAIT 10", f"JOIN {geocode} 0"]
        ]
        run_experiments(topo, iterations, results_dir, analysis_file, actions)
