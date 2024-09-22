from mini.experiments.setup import Setup
from mini.experiments.experiment2 import run_experiment

topoFile = "/spatialsync/mini/experiments/topologies/topology1.conf"

# root_geocode = "DPWHWT"
packet_segment_size = 50
waitTime = 1

if __name__ == "__main__":
    # Setup.root_geocode = root_geocode
    Setup.packet_segment_size = packet_segment_size
    Setup.wait_time = waitTime

    # Setup.add_actions(["WAIT", "ADD /add/data/dpwhwtsh401", "UPDATE"])
    # Setup.add_actions(["INIT DPWHWT"])
    # Setup.add_actions(["WAIT", "JOIN DPWHWT"])
    # Setup.add_actions(["WAIT", "INIT DPWHWT", "UPDATE"])
    Setup.add_actions(["WAIT", "INIT DPWHWT","ADD /add/data/dpwhwtsh401", "UPDATE"])
    Setup.add_actions(["WAIT"])

    run_experiment(topoFile)
