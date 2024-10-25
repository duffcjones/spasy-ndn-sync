import logging
import asyncio
from pympler import asizeof
from random import seed

import Config
from Interests import send_init_interests, send_sync_request
from Util import pack_data
from Spasy import Spasy
from Callbacks import on_direct_root_hash_interest, on_direct_geocode_interest
from Interests import fetch_segments

# TODO Add wait time through function decorator

async def setup(opts):
    logging.info("Initializing interests")
    Config.timer.start_timer(f"init_interests")
    await send_init_interests()
    Config.timer.stop_timer(f"init_interests")

    await asyncio.sleep(int(opts[-1]))
    return


async def init(opts):
    logging.info(f'Action: Init with geocode {opts[0]}')
    Config.spasy = Spasy(opts[0], int(opts[2]))
    #Config.spasy.max_number_recent_updates = int(opts[2])
    Config.spasy.build_tree_from_file(opts[0], Config.config["word_list_path"], int(opts[1]), True)
    Config.geocode = opts[0]
    logging.info(f"Tree created for geocode {opts[0]} with root hashcode {Config.spasy.trees[opts[0]].root.hashcode} with update queue of size {Config.spasy.trees[opts[0]].max_number_recent_updates}")
    logging.info(f"Number of assets: {opts[1]}\n Size: {asizeof.asizeof(Config.spasy.trees[opts[0]])} bytes")

    # Size of full initialized tree uncompressed
    Config.stats.record_stat(f"{Config.config["node_name"]}_initial_tree_size_uncompressed", f"{asizeof.asizeof(Config.spasy.trees[opts[0]])}")
    # Size of initialized tree updates uncompressed
    Config.stats.record_stat(f"{Config.config["node_name"]}_initial_updates_size_uncompressed", f"{asizeof.asizeof(Config.spasy.trees[opts[0]].recent_updates)}")

    # await prep_tree(Config.spasy)

    # Reset seeding for nonce generation
    # seed()

    await asyncio.sleep(int(opts[-1]))
    return

async def register_route(opts):

    geocode_route = Config.config["direct_geocode_prefix"] + f"/{opts[0]}"
    await Config.app.register(geocode_route, on_direct_geocode_interest)
    logging.info(f"Registered route for {geocode_route}")

    return 

async def add(opts):
    logging.info(f"Action: Add data {opts[0]}")

    logging.info("Starting sync_update timer")
    Config.timer.start_global_timer("sync_update")

    Config.timer.start_timer("add_data")
    Config.spasy.add_data_to_tree(Config.geocode, str(opts[0]))
    Config.timer.stop_timer("add_data")

    await asyncio.sleep(int(opts[-1]))
    return


async def join(opts):
    logging.info(f"Action: Join geocode {opts[0]}")

    Config.timer.start_timer(f"{Config.config["node_name"]}_join_update")
    name = Config.config["direct_geocode_prefix"] + f"/{opts[0]}"
    num_seg, received_tree, data = await fetch_segments(name)
    new_tree = received_tree.trees[Config.geocode]
    Config.spasy.add_tree(new_tree)
    Config.timer.stop_timer(f"{Config.config["node_name"]}_join_update")

    Config.timer.start_timer(f"{Config.config['node_name']}_calculate_size")
    #logging.info(f"Receieved tree for geocode {opts[0]} with size {asizeof.asizeof(Config.spasy)}")
    Config.timer.stop_timer(f"{Config.config['node_name']}_calculate_size")
    logging.info(f"Root of tree is {Config.spasy.trees[Config.geocode].root.hashcode}")

    # Size of full tree uncompressed received through join request
    # Config.stats.record_stat(f"{Config.config["node_name"]}_received_tree_size", f"{asizeof.asizeof(received_tree)}")
    # Size of full tree compressed received through join request
    # Config.stats.record_stat(f"{Config.config["node_name"]}_received_compressed_tree_size", f"{asizeof.asizeof(data)}")

    await asyncio.sleep(int(opts[-1]))
    return


async def update(opts):
    logging.info(f"Action: Update")

    # Config.timer.start_timer("prep_queue")
    # await prep_queue(Config.spasy)
    # Config.timer.stop_timer("prep_queue")

    root_hash, seg_cnt = Config.packed_updates_queue[-1]

    sync_requests = []
    Config.timer.start_global_timer(f"notification_interest")
    for route in Config.config["multi_cast_routes"]:
        sync_requests.append(send_sync_request(route, root_hash, seg_cnt))
    await asyncio.gather(*sync_requests)

    await asyncio.sleep(int(opts[-1]))
    return


async def wait(opts):
    logging.info("Action: Waiting")
    await asyncio.sleep(int(opts[0]))
    return


async def prep_tree(opts):
    logging.info(f"Packing tree with hashcode {Config.spasy.trees[Config.geocode].root.hashcode}")

    Config.timer.start_timer(f"prep_tree")

    geocode_route = Config.config["direct_geocode_prefix"] + f"/{Config.geocode}"
    logging.info(f"Packing tree with geocode {Config.geocode}")
    packets, seg_cnt, serialized_data = pack_data(Config.spasy, geocode_route)
    Config.packed_tree_geocode = (packets, seg_cnt)

    Config.timer.stop_timer(f"prep_tree")

    #Size of single tree packet
    # Config.stats.record_stat(f"{Config.config["node_name"]}_tree_packet_size", f"{asizeof.asizeof(packets[0])}")
    # Size of all packets of full tree (after compression)
    # Config.stats.record_stat(f"{Config.config["node_name"]}_compressed_tree_size", f"{sum([asizeof.asizeof(packet) for packet in packets])}")
    # Number of packets
    Config.stats.record_stat(f"num_packets_tree", f"{seg_cnt}")

    await asyncio.sleep(int(opts[-1]))
    return


async def prep_queue(opts):
    logging.info(f"Packing queue with hashcode {Config.spasy.trees[Config.geocode].root.hashcode}")

    Config.timer.start_timer(f"prep_queue")

    # Pack recent updates
    root_hash_route = Config.config["direct_root_hash_prefix"] + f"/{Config.spasy.trees[Config.geocode].root.hashcode}"
    # logging.info(Config.spasy.trees[Config.geocode].recent_updates)
    packets, seg_cnt, serialized_data = pack_data(Config.spasy.trees[Config.geocode].recent_updates, root_hash_route)

    Config.packed_updates_dict[Config.spasy.trees[Config.geocode].root.hashcode] = (packets, seg_cnt)
    Config.packed_updates_queue.append((Config.spasy.trees[Config.geocode].root.hashcode, seg_cnt))

    Config.timer.start_timer("register_root_hash_route")
    await Config.app.register(root_hash_route, on_direct_root_hash_interest)
    Config.timer.stop_timer("register_root_hash_route")
    logging.info(f"Registered route for {root_hash_route}")

    Config.timer.stop_timer("prep_queue")

    # Size of single update packet
    # Config.stats.record_stat(f"{Config.config["node_name"]}_update_packet_size", f"{asizeof.asizeof(packets[0])}")
    # Size of all packets of update list after compression
    # Config.stats.record_stat(f"{Config.config["node_name"]}_compressed_updates_size", f"{sum([asizeof.asizeof(packet) for packet in packets])}")
    # Number of packets
    Config.stats.record_stat(f"num_packets_queue", f"{seg_cnt}")

    await asyncio.sleep(int(opts[-1]))
    return


actions = {
    "SETUP": setup,
    "INIT": init,
    "ADD": add,
    "JOIN": join,
    "UPDATE": update,
    "WAIT": wait,
    "PREP_QUEUE": prep_queue,
    "PREP_TREE": prep_tree,
    "REGISTER_ROUTE": register_route,
}
