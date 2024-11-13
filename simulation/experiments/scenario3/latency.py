from os import path, getcwd

from experiments.setup import Setup
from experiments.experiment import run_experiments
from experiments.util import make_topo, clear_results

results_dir = "scenario3/latency-{}"
experiment_name = "scenario3-latency-{}"

num_nodes = 2
num_mec_nodes = 1
bandwidth = 1000

tree_size = 10000
queue_size = 50
batch_size = 100
geocode = "dpwhwt"
request_asset = True
asset_path = path.join(getcwd(),"resources/beach_ball.glb")

experiment_wait_time = 20

if __name__ == "__main__":
    Setup.batch_size = batch_size
    Setup.request_asset = request_asset

    actions = [
        ["SETUP 2", f"INIT {geocode} {tree_size} {queue_size} 5", "WAIT 10"],
        ["SETUP 2", f'INIT {geocode} {tree_size} {queue_size} 5', f"ADD /alice/ball/_v0/dpwhwtmpz0 {asset_path} 0", "WAIT 10"],
        ["SETUP 2", f"INIT {geocode} {tree_size} {queue_size} 5", "WAIT 10"]
    ]

    latencies = [2, 3, 5, 10, 15]
    # latencies = [2]

    for latency in latencies:
        topo = make_topo(num_nodes, num_mec_nodes, latency, bandwidth)
        run_experiments(topo, results_dir.format(latency), experiment_name.format(latency), actions, experiment_wait_time)
