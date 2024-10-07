from mini.experiments.setup import Setup
from mini.experiments.experiment2 import run_experiments

iterations = 2

topo_file = "/spatialsync/mini/experiments/scenario3/topologies/latency-1.conf"
results_dir = "/spatialsync/mini/experiments/results"
analysis_file = "analysis.csv"

packet_segment_size = 50
waitTime = 1

if __name__ == "__main__":
    Setup.packet_segment_size = packet_segment_size
    Setup.wait_time = waitTime

    Setup.add_actions(["INIT dpwhwt 1", "ADD /add/data/dpwhwtsh401 0", "UPDATE 0"])
    Setup.add_actions(["INIT dpwhwt 1", "ADD /add/data/dpwhwtsh234 0", "UPDATE 0"])
    # Setup.add_actions(["INIT dpwhwt 1", "WAIT 3"])

    run_experiments(topo_file, iterations, results_dir, analysis_file)
