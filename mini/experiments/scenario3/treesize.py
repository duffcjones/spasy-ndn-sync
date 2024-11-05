from mini.experiments.setup import Setup
from mini.experiments.experiment import run_experiments
from mini.experiments.util import make_topo, clear_results

topo_file_base = "/spatialsync/mini/experiments/scenario3/topologies/latency-{}.conf"
results_dir_base = "/spatialsync/mini/experiments/results/scenario3/treesize-{}"
experiment_file = "scenario3-treesize-{}"

packet_segment_size = 8800
batch_size = 75
waitTime = 1
num_nodes = 5
num_mec_nodes = 1
bandwidth = 1000
latency = 2
queue_size = 50
geocode = "dpwhwt"
request_asset = "False"
experimentWaitTime = 65

asset_path = "/spatialsync/mini/experiments/resources/beach_ball.glb"

if __name__ == "__main__":
    Setup.packet_segment_size = packet_segment_size
    Setup.batch_size = batch_size
    Setup.wait_time = waitTime

    tree_sizes = [100, 1000, 5000, 10000, 15000]
    #tree_sizes = [20000, 25000]

    for tree_size in tree_sizes:
        clear_results("/tmp/minindn")
        topo = make_topo(num_nodes, num_mec_nodes, latency, bandwidth)
        results_dir = results_dir_base.format(tree_size)
        actions = [
            ["SETUP 2", f"INIT {geocode} {tree_size} {queue_size} 5", "WAIT 30"],
            ["SETUP 2", f"INIT {geocode} {tree_size} {queue_size} 5", "ADD /alice/ball/_v0/dpwhwtmpz0 {asset_path} 0", "UPDATE 0", "WAIT 30"],
            ["SETUP 2", f"INIT {geocode} {tree_size} {queue_size} 5", "WAIT 30"]
        ]
        run_experiments(topo, results_dir, experiment_file.format(tree_size), actions, experimentWaitTime)
