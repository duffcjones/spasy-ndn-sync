from mini.experiments.setup import Setup
from mini.experiments.experiment2 import run_experiment

topoFile = "/spatialsync/mini/experiments/topologies/topology3.conf"
results_dir = "/spatialsync/mini/experiments/results/"
results_path = results_dir + "results3.csv"

packet_segment_size = 1500
waitTime = 1

if __name__ == "__main__":
    Setup.packet_segment_size = packet_segment_size
    Setup.wait_time = waitTime

    Setup.add_actions(["INIT dpwhwt 1", "ADD /add/data/dpwhwtsh401 0", "UPDATE 0"])
    Setup.add_actions(["INIT dpwhwt 1", "ADD /add/data/dpwhwtsh234 0", "UPDATE 0"])
    # Setup.add_actions(["INIT dpwhwt 1", "WAIT 3"])

    run_experiment(topoFile, results_dir, results_path)
