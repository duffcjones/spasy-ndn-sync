import logging
import asyncio
from pympler import asizeof
from random import seed
import os

from ndn.encoding import Name, Component

import Config
from Interests import send_init_interests, send_sync_request
from Util import pack_data
from Spasy import Spasy
from Callbacks import on_direct_root_hash_interest, on_direct_geocode_interest, on_direct_asset_interest
from Interests import fetch_segments
from Interests import fetch_segments_batch


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
    Config.spasy.build_tree_from_file(opts[0], Config.config["word_list_path"], int(opts[1]), True)
    Config.geocode = opts[0]
    logging.info(f"Tree created for geocode {opts[0]} with root hashcode {Config.spasy.trees[opts[0]].root.hashcode} with update queue of size {Config.spasy.trees[opts[0]].max_number_recent_updates}")
    logging.info(f"Number of assets: {opts[1]}\n Size: {asizeof.asizeof(Config.spasy.trees[opts[0]])} bytes")

    # Size of full initialized tree uncompressed
    Config.stats.record_stat(f"{Config.config["node_name"]}_initial_tree_size_uncompressed", f"{asizeof.asizeof(Config.spasy.trees[opts[0]])}")
    # Size of initialized tree updates uncompressed
    Config.stats.record_stat(f"{Config.config["node_name"]}_initial_updates_size_uncompressed", f"{asizeof.asizeof(Config.spasy.trees[opts[0]].recent_updates)}")

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
    logging.info(f"Action: Add data {opts[0]} at path {opts[1]}")

    logging.info("Starting sync_update timer")
    Config.timer.start_global_timer("sync_update")
    if Config.config["request_asset"] == "True":
        Config.timer.start_global_timer("sync_update_data")

    Config.timer.start_timer("add_data")
    Config.spasy.add_data_to_tree(Config.geocode, str(opts[0]))
    Config.timer.stop_timer("add_data")

    task = asyncio.create_task(prep_queue(opts[0]))
    task = asyncio.create_task(prep_asset(opts[0], opts[1]))
    task = asyncio.create_task(update(opts[0]))

    await asyncio.sleep(int(opts[-1]))
    return


async def join(opts):
    logging.info(f"Action: Join geocode {opts[0]}")

    Config.timer.start_timer(f"join_update")
    name = Config.config["direct_geocode_prefix"] + f"/{opts[0]}"

    batch_size = int(Config.config["batch_size"])
    if batch_size > 0:
        num_seg, received_tree, data = await fetch_segments_batch(name,batch_size)
    else:
        num_seg, received_tree, data = await fetch_segments(name)

    new_tree = received_tree.trees[Config.geocode]
    Config.spasy.add_tree(new_tree)
    Config.timer.stop_timer(f"join_update")

    Config.timer.start_timer(f"calculate_size")
    logging.info(f"Receieved tree for geocode {opts[0]} with size {asizeof.asizeof(Config.spasy)}")
    Config.timer.stop_timer(f"calculate_size")
    logging.info(f"Root of tree is {Config.spasy.trees[Config.geocode].root.hashcode}")

    # Size of full tree uncompressed received through join request
    Config.stats.record_stat(f"{Config.config["node_name"]}_received_tree_size", f"{asizeof.asizeof(received_tree)}")
    # Size of full tree compressed received through join request
    Config.stats.record_stat(f"{Config.config["node_name"]}_received_compressed_tree_size", f"{asizeof.asizeof(data)}")

    await asyncio.sleep(int(opts[-1]))
    return


async def update(opts):
    logging.info(f"Action: Update")

    root_hash, seg_cnt, asset_name = Config.packed_updates_queue[-1]

    sync_requests = []
    Config.timer.start_global_timer(f"notification_interest")
    for route in Config.config["multi_cast_routes"]:
        sync_requests.append(send_sync_request(route, root_hash, asset_name, seg_cnt))
    await asyncio.gather(*sync_requests)

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

    # Number of packets
    Config.stats.record_stat(f"num_packets_tree", f"{seg_cnt}")

    await asyncio.sleep(int(opts[-1]))
    return


async def prep_queue(asset_name):
    logging.info(f"Packing queue with hashcode {Config.spasy.trees[Config.geocode].root.hashcode} with asset {asset_name}")

    Config.timer.start_timer(f"prep_queue")

    # Pack recent updates
    root_hash_route = Config.config["direct_root_hash_prefix"] + f"/{Config.spasy.trees[Config.geocode].root.hashcode}"
    packets, seg_cnt, serialized_data = pack_data(Config.spasy.trees[Config.geocode].recent_updates, root_hash_route)

    Config.packed_updates_dict[Config.spasy.trees[Config.geocode].root.hashcode] = (packets, seg_cnt, asset_name)
    Config.packed_updates_queue.append((Config.spasy.trees[Config.geocode].root.hashcode, seg_cnt, asset_name))

    Config.timer.start_timer("register_root_hash_route")
    await Config.app.register(root_hash_route, on_direct_root_hash_interest)
    Config.timer.stop_timer("register_root_hash_route")
    logging.info(f"Registered route for {root_hash_route}")

    Config.timer.stop_timer("prep_queue")

    # Number of packets
    Config.stats.record_stat(f"num_packets_queue", f"{seg_cnt}")

    return

async def prep_asset(asset_name, asset_path):
    Config.timer.start_timer("prep_asset")
    asset_route = Config.config["direct_asset_prefix"] + asset_name
    logging.info(f"Packing asset with name {asset_route}")

    with open(asset_path, 'rb') as f:
        data = f.read()
        seg_cnt = (len(data) + Config.config["packet_segment_size"]- 1) // Config.config["packet_segment_size"]
        packets = [Config.app.prepare_data(Name.normalize(asset_route) + [Component.from_segment(i)],
                                    data[i*Config.config["packet_segment_size"]:(i+1)*Config.config["packet_segment_size"]],
                                    freshness_period=10000,
                                    final_block_id=Component.from_segment(seg_cnt - 1))
                   for i in range(seg_cnt)]
    logging.info(f'Created {seg_cnt} chunks under name {Name.to_str(asset_route)}')
    Config.stats.record_stat(f"num_packets_asset", f"{seg_cnt}")


    Config.packed_assets_dict[asset_name] = (packets, seg_cnt)
    Config.timer.stop_timer("prep_asset")

    Config.timer.start_timer("register_asset_route")
    await Config.app.register(asset_route, on_direct_asset_interest)
    Config.timer.stop_timer("register_asset_route")
    logging.info(f"Registered route for {asset_route}")

    return


actions = {
    "SETUP": setup,
    "INIT": init,
    "ADD": add,
    "JOIN": join,
    "UPDATE": update,
    "WAIT": wait,
    "PREP_TREE": prep_tree,
    "REGISTER_ROUTE": register_route,
}
