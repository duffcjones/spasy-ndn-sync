from mini.experiments.setup import Setup
from mini.experiments.experiment2 import run_experiment

topoFile = "/spatialsync/mini/experiments/topologies/topology1.conf"
results_dir = "/spatialsync/mini/experiments/results/"
results_path = results_dir + "results1.csv"

packet_segment_size = 500
waitTime = 1

if __name__ == "__main__":
    Setup.packet_segment_size = packet_segment_size
    Setup.wait_time = waitTime

    Setup.add_actions(["INIT dpwhwt 0"])
    Setup.add_actions(["WAIT 1", "JOIN dpwhwt 0"])

    run_experiment(topoFile, results_dir, results_path)
