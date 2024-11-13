from experiments.setup import Setup
from experiments.experiment import run_experiments
from experiments.util import make_topo, clear_results

results_dir = "scenario1/nodes-{}"
experiment_name = "scenario1-node-{}"

packet_segment_size = 8800
batch_size = 0
waitTime = 1
bandwidth = 1000
latency = 2
tree_size = 100
queue_size = 50
geocode = "dpwhwt"
experimentWaitTime = 20
num_mec_nodes = 25

if __name__ == "__main__":
    Setup.packet_segment_size = packet_segment_size
    Setup.batch_size = batch_size
    Setup.wait_time = waitTime

    num_nodes = [3,5,10,15,19]


    for num_node in num_nodes:
        topo = make_topo(num_node, num_mec_nodes, latency, bandwidth)
        actions = [
            [f"INIT {geocode} {tree_size} {queue_size} 0", f"REGISTER_ROUTE {geocode}", "PREP_TREE 0", "WAIT 10"],
            [ f"INIT {geocode} {tree_size} {queue_size} 0", f"REGISTER_ROUTE {geocode}", "PREP_TREE 0",
             "WAIT 10"],
            [f"INIT {geocode} {tree_size} {queue_size} 0", f"REGISTER_ROUTE {geocode}", "PREP_TREE 0",
             "WAIT 10"],
            [f"INIT {geocode} {tree_size} {queue_size} 0", f"REGISTER_ROUTE {geocode}", "PREP_TREE 0",
             "WAIT 10"],
            [f"INIT {geocode} {tree_size} {queue_size} 0", f"REGISTER_ROUTE {geocode}", "PREP_TREE 0",
             "WAIT 10"],
            [f"INIT {geocode} {tree_size} {queue_size} 0", f"REGISTER_ROUTE {geocode}", "PREP_TREE 0",
             "WAIT 10"],
            [f"INIT {geocode} {tree_size} {queue_size} 0", f"REGISTER_ROUTE {geocode}", "PREP_TREE 0",
             "WAIT 10"],
            [f"INIT {geocode} {tree_size} {queue_size} 0", f"REGISTER_ROUTE {geocode}", "PREP_TREE 0",
             "WAIT 10"],
            [f"INIT {geocode} {tree_size} {queue_size} 0", f"REGISTER_ROUTE {geocode}", "PREP_TREE 0",
             "WAIT 10"],
            [f"INIT {geocode} {tree_size} {queue_size} 0", f"REGISTER_ROUTE {geocode}", "PREP_TREE 0",
             "WAIT 10"],
            [f"INIT {geocode} {tree_size} {queue_size} 0", f"REGISTER_ROUTE {geocode}", "PREP_TREE 0", "WAIT 10"],
            [f"INIT {geocode} {tree_size} {queue_size} 0", f"REGISTER_ROUTE {geocode}", "PREP_TREE 0",
             "WAIT 10"],
            [f"INIT {geocode} {tree_size} {queue_size} 0", f"REGISTER_ROUTE {geocode}", "PREP_TREE 0",
             "WAIT 10"],
            [f"INIT {geocode} {tree_size} {queue_size} 0", f"REGISTER_ROUTE {geocode}", "PREP_TREE 0",
             "WAIT 10"],
            [f"INIT {geocode} {tree_size} {queue_size} 0", f"REGISTER_ROUTE {geocode}", "PREP_TREE 0",
             "WAIT 10"],
            [f"INIT {geocode} {tree_size} {queue_size} 0", f"REGISTER_ROUTE {geocode}", "PREP_TREE 0",
             "WAIT 10"],
            [f"INIT {geocode} {tree_size} {queue_size} 0", f"REGISTER_ROUTE {geocode}", "PREP_TREE 0",
             "WAIT 10"],
            [f"INIT {geocode} {tree_size} {queue_size} 0", f"REGISTER_ROUTE {geocode}", "PREP_TREE 0",
             "WAIT 10"],
            [f"INIT {geocode} {tree_size} {queue_size} 0", f"REGISTER_ROUTE {geocode}", "PREP_TREE 0",
             "WAIT 10"],
            [f"INIT {geocode} {tree_size} {queue_size} 0", f"REGISTER_ROUTE {geocode}", "PREP_TREE 0",
             "WAIT 10"],
            [f"INIT {geocode} {tree_size} {queue_size} 0", f"REGISTER_ROUTE {geocode}", "PREP_TREE 0",
             "WAIT 10"],
            [f"INIT {geocode} {tree_size} {queue_size} 0", f"REGISTER_ROUTE {geocode}", "PREP_TREE 0",
             "WAIT 10"],
            [f"INIT {geocode} {tree_size} {queue_size} 0", f"REGISTER_ROUTE {geocode}", "PREP_TREE 0",
             "WAIT 10"],
            [f"INIT {geocode} {tree_size} {queue_size} 0", f"REGISTER_ROUTE {geocode}", "PREP_TREE 0",
             "WAIT 10"],
            [f"INIT {geocode} {tree_size} {queue_size} 0", f"REGISTER_ROUTE {geocode}", "PREP_TREE 0",
             "WAIT 10"],
            [f"INIT {geocode} 1 1 10", f"JOIN {geocode} 0", "WAIT 10"],
            [f"INIT {geocode} 1 1 10", "WAIT 10"],
        ]

        run_experiments(topo, results_dir.format(num_node), experiment_name.format(num_node), actions,  experimentWaitTime)
