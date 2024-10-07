from mininet.topo import Topo
import shutil
from pathlib import Path

def make_topo(num_nodes,latency,bandwidth):
    print(f"Making topology with {num_nodes} nodes and {latency}ms latency with bandwidth {bandwidth}")
    topo = Topo()

    user_nodes = []
    mec_node = topo.addHost("h0")

    for i in range(1, num_nodes):
        node_name = f"h{i}"
        node = topo.addHost(node_name)
        print(f"Added node {node_name}")
        user_nodes.append(node)

    for user_node in user_nodes:
        topo.addLink(mec_node, user_node, delay=f"{latency}ms", bw=bandwidth)

    return topo

def clear_results(directory):
    directory = Path(directory)
    if directory.is_dir():
        for item in directory.iterdir():
            if item.is_dir():
                clear_results(item)
            else:
                item.unlink()
        directory.rmdir()
