from os import path, getcwd

from experiments.setup import Setup
from experiments.experiment import run_experiments
from experiments.util import make_topo, clear_results

results_dir = "scenario3/updatesize-{}"
experiment_file = "scenario3-updatesize-{}"

num_nodes = 2
num_mec_nodes = 1
bandwidth = 1000
latency = 2

tree_size = 10000
batch_size = 100
geocode = "dpwhwt"
request_asset = False
asset_path = path.join(getcwd(), "resources/beach_ball.glb")

experiment_wait_time = 15

if __name__ == "__main__":
    Setup.batch_size = batch_size
    Setup.request_asset = request_asset

    queue_sizes = [10, 25, 50, 100, 250]

    for queue_size in queue_sizes:
        topo = make_topo(num_nodes, num_mec_nodes, latency, bandwidth)

        actions = [
            ["SETUP 2", f"INIT {geocode} {tree_size} {queue_size} 5", "WAIT 5"],
            ["SETUP 2", f"INIT {geocode} {tree_size} {queue_size} 5", f"ADD /alice/ball/_v0/dpwhwtmpz0 {asset_path} 0", "WAIT 5"],
            ["SETUP 2", f"INIT {geocode} {tree_size} {queue_size} 5", "WAIT 5"]
        ]

        run_experiments(topo, results_dir.format(queue_size), experiment_file.format(queue_size), actions, experiment_wait_time)
