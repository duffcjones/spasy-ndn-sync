import logging
import asyncio
import pickle
import sys

import Config
from Interests import send_init_interests, send_sync_request
from Util import pack_tree
from Spasy import Spasy
from Callbacks import on_direct_root_hash_interest, on_direct_geocode_interest
from Interests import fetch_segments


# TODO Add wait time through function decorator

async def init(opts):
    logging.info(f'Action: Init with geocode {opts[0]}')
    Config.spasy = Spasy(opts[0])
    Config.geocode = opts[0]
    logging.info(f"Tree created for geocode {opts[0]} with root hashcode {Config.spasy.tree.root.hashcode} with size {sys.getsizeof(Config.spasy)} bytes")

    await prep_tree()

    geocode_route = Config.config["direct_geocode_prefix"] + f"/{opts[0]}"
    await Config.app.register(geocode_route, on_direct_geocode_interest)
    logging.info(f"Registered route for {geocode_route}")

    await asyncio.sleep(int(opts[-1]))
    return


async def add(opts):
    logging.info(f"Action: Add data {opts[0]}")

    Config.timer.start_timer("sync_update")
    Config.spasy.add_data_to_tree(opts[0])

    await prep_tree()

    await asyncio.sleep(int(opts[-1]))
    return


async def join(opts):
    logging.info(f"Action: Join geocode {opts[0]}")
    Config.timer.start_timer(f"{Config.config["node_name"]}_join_update")
    name = Config.config["direct_geocode_prefix"] + f"/{opts[0]}"
    num_seg, received_tree = await fetch_segments(name)
    Config.spasy = received_tree
    Config.timer.stop_timer(f"{Config.config["node_name"]}_join_update")
    logging.info(f"Receieved tree for geocode {opts[0]}")

    await asyncio.sleep(int(opts[-1]))
    return


async def update(opts):
    logging.info("Action: Update")

    root_hash, seg_cnt = Config.packed_trees_queue[-1]

    sync_requests = []
    for route in Config.config["multi_cast_routes"]:
        task = asyncio.create_task(send_sync_request(route, root_hash, seg_cnt))
        sync_requests.append(task)

    await asyncio.sleep(int(opts[-1]))
    return


async def wait(opts):
    logging.info("Action: Waiting")
    await asyncio.sleep(int(opts[0]))
    return


async def prep_tree():
    logging.info(f"Packing tree with hashcode {Config.spasy.tree.root.hashcode}")

    root_hash_route = Config.config["direct_root_hash_prefix"] + f"/{Config.spasy.tree.root.hashcode}"
    packets, seg_cnt = pack_tree(Config.spasy, root_hash_route)
    Config.packed_trees_hashcode_dict[Config.spasy.tree.root.hashcode] = (packets, seg_cnt)
    Config.packed_trees_queue.append((Config.spasy.tree.root.hashcode, seg_cnt))


    await Config.app.register(root_hash_route, on_direct_root_hash_interest)
    logging.info(f"Registered route for {root_hash_route}")

    geocode_route = Config.config["direct_geocode_prefix"] + f"/{Config.geocode}"
    logging.info(f"Packing tree with geocode {Config.geocode}")
    packets, seg_cnt = pack_tree(Config.spasy, geocode_route)
    Config.packed_tree_geocode = (packets, seg_cnt)
    return


actions = {
    "INIT": init,
    "ADD": add,
    "JOIN": join,
    "UPDATE": update,
    "WAIT": wait
}
