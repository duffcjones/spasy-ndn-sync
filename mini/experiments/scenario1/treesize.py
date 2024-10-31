from mini.experiments.setup import Setup
from mini.experiments.experiment import run_experiments
from mini.experiments.util import make_topo, clear_results

topo_file_base = "/spatialsync/mini/experiments/scenario1/topologies/latency-{}.conf"
results_dir_base = "/spatialsync/mini/experiments/results/scenario1/treesize-{}"
experiment_file = "scenario1-treesize-{}"

packet_segment_size = 8800
batch_size = 100
waitTime = 1
num_nodes = 3
bandwidth = 1000
latency = 2
queue_size = 50
geocode = "dpwhwt"
experimentWaitTime = 60

if __name__ == "__main__":
    Setup.packet_segment_size = packet_segment_size
    Setup.batch_size = batch_size
    Setup.wait_time = waitTime

    # tree_sizes = [10,100,1000,10000,50000]
    tree_sizes = [15000, 20000]

    for tree_size in tree_sizes:
        clear_results("/tmp/minindn")
        topo = make_topo(num_nodes, latency, bandwidth)
        results_dir = results_dir_base.format(tree_size)
        actions = [
            ["SETUP 2", f"INIT {geocode} {tree_size} {queue_size} 0", f"REGISTER_ROUTE {geocode}", "PREP_TREE 0", "WAIT 10"],
            ["SETUP 2", f"INIT {geocode} {tree_size} {queue_size} 0", f"REGISTER_ROUTE {geocode}", "PREP_TREE 0", "WAIT 10"],
            ["SETUP 2",f"INIT {geocode} 1 1 10", f"JOIN {geocode} 0", "WAIT 10"]
        ]

        run_experiments(topo, results_dir, experiment_file.format(tree_size), actions, experimentWaitTime)
