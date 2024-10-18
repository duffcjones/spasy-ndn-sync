from mini.experiments.setup import Setup
from mini.experiments.experiment2 import run_experiments
from mini.experiments.util import make_topo, clear_results

iterations = 25

topo_file_base = "/spatialsync/mini/experiments/scenario2/topologies/latency-{}.conf"
results_dir_base = "/spatialsync/mini/experiments/results/scenario2/latency-{}"
experiment_name = "scenario2-latency-{}"

packet_segment_size = 2000
waitTime = 5
num_nodes = 5
bandwidth = 1000
tree_size = 1000
queue_size = 100
geocode = "dpwhwt"

if __name__ == "__main__":
    Setup.packet_segment_size = packet_segment_size
    Setup.wait_time = waitTime

    actions = [
        ["SET 2", f"INIT {geocode} {tree_size} {queue_size} 5", "ADD /add/data/dpwhwtsh401 0", "UPDATE 0", "WAIT 10"],
        ["SET 2", f"INIT {geocode} {tree_size} {queue_size} 5", "WAIT 10"]
    ]

    # latencies = [1,2,3,5,10]
    latencies = [1]
    for latency in latencies:
        # clear_results("/tmp/minindn")
        topo = make_topo(num_nodes, latency, bandwidth)
        results_dir = results_dir_base.format(latency)
        # run_experiments(topo_file_base.format(latency), iterations, results_dir, experiment_name.format(latency), actions, 22)
        run_experiments(topo, iterations, results_dir, experiment_name.format(latency), actions, 30)
