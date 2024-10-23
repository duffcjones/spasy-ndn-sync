from mini.experiments.setup import Setup
from mini.experiments.experiment import run_experiments
from mini.experiments.util import make_topo, clear_results

iterations = 10

topo_file_base = "/spatialsync/mini/experiments/scenario2/topologies/latency-{}.conf"
results_dir_base = "/spatialsync/mini/experiments/results/scenario2/latency-{}"
experiment_name = "scenario2-latency-{}"

packet_segment_size = 8800
waitTime = 5
num_nodes = 5
bandwidth = 1000
tree_size = 10000
queue_size = 25
geocode = "dpwhwt"
experimentWaitTime = 30

if __name__ == "__main__":
    Setup.packet_segment_size = packet_segment_size
    Setup.wait_time = waitTime

    actions = [
        ["SETUP 2", f"INIT {geocode} {tree_size} {queue_size} 5", "ADD /some/test/data/dpwhwtmpz0 0","PREP_QUEUE 0", "UPDATE 0", "WAIT 10"],
        ["SETUP 2", f"INIT {geocode} {tree_size} {queue_size} 5", "WAIT 10"]
    ]

    # latencies = [1,2,3,5,10]
    latencies = [2]
    for latency in latencies:
        clear_results("/tmp/minindn")
        topo = make_topo(num_nodes, latency, bandwidth)
        results_dir = results_dir_base.format(latency)
        # run_experiments(topo_file_base.format(latency), iterations, results_dir, experiment_name.format(latency), actions, experimentWaitTime)
        run_experiments(topo, iterations, results_dir, experiment_name.format(latency), actions, experimentWaitTime)
