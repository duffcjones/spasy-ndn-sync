from mininet.topo import Topo
from pathlib import Path
from collections import deque

def make_topo(num_nodes,num_mec_nodes,latency,bandwidth):
    print(f"Making topology with {num_nodes} nodes, {num_mec_nodes} mec nodes and {latency}ms latency with bandwidth {bandwidth}")
    topo = Topo()

    user_nodes = deque()
    mec_nodes = deque()

    for i in range(num_mec_nodes):
        print(f"Added mec_node h{i}")
        mec_node = topo.addHost(f"h{i}")
        if len(mec_nodes) > 1:
            topo.addLink(mec_node,mec_nodes[-1], delay=f"{latency}ms", bw=bandwidth, loss=0, max_queue_size=1000)
        mec_nodes.append(mec_node)

    if len(mec_nodes) > 1:
        topo.addLink(mec_nodes[0],mec_nodes[-1], delay=f"{latency}ms", bw=bandwidth, loss=0, max_queue_size=1000)

    for i in range(num_nodes):
        node_name = f"h{i + num_mec_nodes}"
        node = topo.addHost(node_name)
        print(f"Added node {node_name}")
        user_nodes.append(node)

    nodes_per_mec = num_nodes // num_mec_nodes
    while mec_nodes:
        mec_node = mec_nodes.popleft()
        num_nodes_added = 0
        while num_nodes_added < nodes_per_mec and user_nodes:
            user_node = user_nodes.popleft()
            topo.addLink(mec_node, user_node, delay=f"{latency}ms", bw=bandwidth, loss=0, max_queue_size=1000)
            num_nodes_added += 1

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