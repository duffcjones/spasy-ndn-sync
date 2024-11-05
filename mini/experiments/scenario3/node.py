from mini.experiments.setup import Setup
from mini.experiments.experiment import run_experiments
from mini.experiments.util import make_topo, clear_results

topo_file_base = "/spatialsync/mini/experiments/scenario3/topologies/nodes-{}.conf"
results_dir_base = "/spatialsync/mini/experiments/results/scenario3/nodes-{}"
experiment_name = "scenario3-node-{}"

packet_segment_size = 8800
batch_size = 100
waitTime = 5
bandwidth = 1000
latency = 2
tree_size = 10000
queue_size = 50
geocode = "dpwhwt"
request_asset = "True"
experimentWaitTime = 15
num_mec_nodes = 1

asset_path = "/spatialsync/mini/experiments/resources/beach_ball.glb"

if __name__ == "__main__":
    Setup.packet_segment_size = packet_segment_size
    Setup.batch_size = batch_size
    Setup.wait_time = waitTime

    num_nodes = [3,5,10]
    #num_nodes = [15, 19]

    for num_node in num_nodes:
        clear_results("/tmp/minindn")
        #num_mec_nodes = num_node // 10
        topo = make_topo(num_node, num_mec_nodes, latency, bandwidth)
        results_dir = results_dir_base.format(num_node)
        actions = [
            ["SETUP 2", f"INIT {geocode} {tree_size} {queue_size} 5", "WAIT 5"],
            ["SETUP 2", f"INIT {geocode} {tree_size} {queue_size} 5", "ADD /alice/ball/_v0/dpwhwtmpz0 {asset_path} 0", "UPDATE 0", "WAIT 5"],
            ["SETUP 2", f"INIT {geocode} {tree_size} {queue_size} 5", "WAIT 5"]
        ]
        run_experiments(topo, results_dir, experiment_name.format(num_node), actions, experimentWaitTime)
