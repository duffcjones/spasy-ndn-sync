from mini.experiments.setup import Setup
from mini.experiments.experiment2 import run_experiments
from mini.experiments.util import make_topo, clear_results

iterations = 10

topo_file_base = "/spatialsync/mini/experiments/scenario1/topologies/nodes-{}.conf"
results_dir_base = "/spatialsync/mini/experiments/results/scenario2/nodes-{}"
experiment_name = "scenario2-node-{}"

packet_segment_size = 8800
waitTime = 1
bandwidth = 1000
latency = 2
tree_size = 1000
queue_size = 100
geocode = "dpwhwt"

if __name__ == "__main__":
    Setup.packet_segment_size = packet_segment_size
    Setup.wait_time = waitTime

    # num_nodes = [5, 10, 15, 20]
    num_nodes = [10]

    for num_node in num_nodes:
        clear_results("/tmp/minindn")
        topo = make_topo(num_node, latency, bandwidth)
        results_dir = results_dir_base.format(num_node)
        actions = [
            [f"INIT {geocode} {tree_size} {queue_size} 30", "ADD /add/data/dpwhwtsh401 0", "UPDATE 0", "WAIT 30"],
            [f"INIT {geocode} {tree_size} {queue_size} 30", "WAIT 30"]
        ]
        run_experiments(topo, iterations, results_dir, experiment_name.format(num_node), actions, 70)
