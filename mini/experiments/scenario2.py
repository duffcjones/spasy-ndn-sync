from mini.experiments.setup import Setup
from mini.experiments.experiment import run_experiment

topoFile = "/spatialsync/mini/experiments/topologies/topology2.conf"

root_geocode = "DPWHWT"
packet_segment_size = 50
waitTime = 1

if __name__ == "__main__":
    Setup.root_geocode = root_geocode
    Setup.packet_segment_size = packet_segment_size
    Setup.wait_time = waitTime

    Setup.add_actions(["WAIT", "UPDATE"])
    Setup.add_actions(["WAIT", "WAIT"])

    run_experiment(topoFile)
