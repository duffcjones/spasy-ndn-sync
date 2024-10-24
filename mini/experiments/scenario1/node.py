from mini.experiments.setup import Setup
from mini.experiments.experiment import run_experiments
from mini.experiments.util import make_topo, clear_results

iterations = 1

topo_file_base = "/spatialsync/mini/experiments/scenario1/topologies/nodes-{}.conf"
results_dir_base = "/spatialsync/mini/experiments/results/scenario1/nodes-{}"
experiment_name = "scenario1-node-{}"

packet_segment_size = 8800
waitTime = 1
# num_nodes = 2
bandwidth = 1000
latency = 2
tree_size = 25000
queue_size = 50
geocode = "dpwhwt"
experimentWaitTime = 15

if __name__ == "__main__":
    Setup.packet_segment_size = packet_segment_size
    Setup.wait_time = waitTime

    # num_nodes = [5, 10, 15, 20]
    num_nodes = [15]

    for num_node in num_nodes:
        clear_results("/tmp/minindn")
        topo = make_topo(num_node, latency, bandwidth)
        results_dir = results_dir_base.format(num_node)
        actions = [
            ["SETUP 2",f"INIT {geocode} 1 1 5", "WAIT 5"],
            ["SETUP 2", f"INIT {geocode} {tree_size} {queue_size} 0", "PREP_TREE 0", "WAIT 5"],
            ["SETUP 2",f"INIT {geocode} 1 1 5", f"JOIN {geocode} 0", "WAIT 5"]
        ] 

        run_experiments(topo, iterations, results_dir, experiment_name.format(num_node), actions,  experimentWaitTime)
