from experiments.setup import Setup
from experiments.experiment import run_experiments
from experiments.util import make_topo, clear_results

results_dir = "scenario1/nodes-{}"
experiment_name = "scenario1-node-{}"

bandwidth = 1000
latency = 2

tree_size = 100
queue_size = 50
batch_size = 0
geocode = "dpwhwt"

experiment_wait_time = 20


if __name__ == "__main__":
    Setup.batch_size = batch_size

    num_nodes = [3, 5, 10, 15, 19]

    for num_node in num_nodes:
        num_mec_nodes = max(num_node // 5, 1)
        topo = make_topo(num_node, num_mec_nodes, latency, bandwidth)

        actions = []
        for i in range(num_mec_nodes):
            actions.append([f"INIT {geocode} {tree_size} {queue_size} 0", f"SERVE_TREE {geocode} 0", "WAIT 10"])
        actions += [
            [f"INIT {geocode} 1 1 10", f"JOIN {geocode} 0", "WAIT 10"],
            [f"INIT {geocode} 1 1 10", "WAIT 10"],
        ]

        run_experiments(topo, results_dir.format(num_node), experiment_name.format(num_node), actions,  experiment_wait_time)
