from mini.experiments.setup import Setup
from mini.experiments.experiment import run_experiments
from mini.experiments.util import make_topo, clear_results

topo_file_base = "/spatialsync/mini/experiments/scenario3/topologies/latency-{}.conf"
results_dir_base = "/spatialsync/mini/experiments/results/scenario3/updatesize-{}"
experiment_file = "scenario3-updatesize-{}"

packet_segment_size = 8800
batch_size = 100
waitTime = 1
num_nodes = 5
num_mec_nodes = 1
bandwidth = 1000
latency = 2
tree_size = 10000
geocode = "dpwhwt"
request_asset = "True"
experimentWaitTime = 15

asset_path = "/spatialsync/mini/experiments/resources/beach_ball.glb"

if __name__ == "__main__":
    Setup.packet_segment_size = packet_segment_size
    Setup.batch_size = batch_size
    Setup.wait_time = waitTime

    queue_sizes = [10,25,50,100,250]
    #queue_sizes = [200]

    for queue_size in queue_sizes:
        clear_results("/tmp/minindn")
        topo = make_topo(num_nodes, num_mec_nodes, latency, bandwidth)
        results_dir = results_dir_base.format(queue_size)
        actions = [
            ["SETUP 2", f"INIT {geocode} {tree_size} {queue_size} 5", "WAIT 5"],
            ["SETUP 2", f"INIT {geocode} {tree_size} {queue_size} 5", f"ADD /alice/ball/_v0/dpwhwtmpz0 {asset_path} 0", "WAIT 5"],
            ["SETUP 2", f"INIT {geocode} {tree_size} {queue_size} 5", "WAIT 5"]
        ]
        run_experiments(topo, results_dir, experiment_file.format(queue_size), actions, experimentWaitTime)
