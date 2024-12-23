import logging
import asyncio
from pympler import asizeof
from random import seed
import pickle

from ndn.encoding import Name, Component

import Config
from Interests import send_init_interests, send_sync_request, fetch_segments, fetch_segments_batch
from Util import pack_data
from Spasy import Spasy
from Callbacks import on_direct_root_hash_interest, on_direct_geocode_interest, on_direct_asset_interest

type Options = list[str]


async def setup(opts: Options) -> None:
    """
    Initialize FIB tables by sending interests to all nodes (can sometimes improve results)

    Args:
        opts: Action options:
                opts[-1] = wait time after action
    """

    logging.info("Initializing interests")

    Config.timer.start_timer(f"init_interests")
    await send_init_interests()
    Config.timer.stop_timer(f"init_interests")

    await asyncio.sleep(int(opts[-1]))
    return


async def init(opts: Options) -> None:
    """
    Initialize SPASY

    Args:
        opts: Action options:
                opts[0] = geocode to initialize tree with,
                opts[1] = tree size,
                opts[2] = queue size,
                opts[-1] = wait time after action
    """

    logging.info(f'Action: Init with geocode {opts[0]}')

    Config.spasy = Spasy(opts[0], int(opts[2]))
    if Config.config["build_tree_method"] == "file":
        Config.spasy.build_tree_from_file(opts[0], Config.config["word_list_path"], int(opts[1]), Config.config["use_timestamp"])
    elif Config.config["build_tree_method"] == "random":
        Config.spasy.build_tree(opts[0], int(opts[1]), Config.config["use_timestamp"])
        # Reset seeding for nonce generation
        seed()

    Config.geocode = opts[0]
    logging.info(f"Tree created for geocode {opts[0]} with root hashcode {Config.spasy.trees[opts[0]].root.hashcode} with update queue of size {Config.spasy.trees[opts[0]].max_number_recent_updates}")
    logging.info(f"Number of assets: {opts[1]}\n Size: {asizeof.asizeof(Config.spasy.trees[opts[0]])} bytes")

    # Size of full initialized tree uncompressed
    Config.stats.record_stat(f"{Config.config["node_name"]}_initial_tree_size_uncompressed", f"{asizeof.asizeof(Config.spasy.trees[opts[0]])}")
    # Size of initialized tree updates uncompressed
    Config.stats.record_stat(f"{Config.config["node_name"]}_initial_updates_size_uncompressed", f"{asizeof.asizeof(Config.spasy.trees[opts[0]].recent_updates)}")

    await asyncio.sleep(int(opts[-1]))
    return


async def add(opts: Options) -> None:
    """
    Add asset to tree and start sync process to update other nodes

    Args:
        opts: Action options:
                opts[0] = Name of new asset,
                opts[1] = Location of asset on disk,
                opts[-1] = wait time after action
    """

    logging.info(f"Action: Add data {opts[0]} at path {opts[1]}")

    logging.info("Starting sync_update timer")
    Config.timer.start_global_timer("sync_update")
    if Config.config["request_asset"]:
        Config.timer.start_global_timer("sync_update_data")

    Config.timer.start_timer("add_data")
    Config.spasy.add_data_to_tree(Config.geocode, str(opts[0]))
    Config.timer.stop_timer("add_data")

    task = asyncio.create_task(prep_queue(opts[0]))
    if Config.config["request_asset"]:
        task = asyncio.create_task(prep_asset(opts[0], opts[1]))
    task = asyncio.create_task(update())

    await asyncio.sleep(int(opts[-1]))
    return


async def join(opts: Options) -> None:
    """
    Join a sync group using a geocode

    Args:
        opts: Action options:
                opts[0] = Geocode of sync group to join,
                opts[-1] = wait time after action
    """

    logging.info(f"Action: Join geocode {opts[0]}")

    Config.timer.start_timer(f"join_update")
    name = Config.config["direct_geocode_prefix"] + f"/{opts[0]}"

    batch_size = int(Config.config["batch_size"])
    if batch_size > 0:
        data, num_seg = await fetch_segments_batch(name, batch_size)
    else:
        data, num_seg = await fetch_segments(name)

    received_tree = pickle.loads(data)
    Config.spasy.add_tree(received_tree)
    Config.timer.stop_timer(f"join_update")

    logging.info(f"Receieved tree for geocode {opts[0]} with size {asizeof.asizeof(Config.spasy)}")
    logging.info(f"Root of tree is {Config.spasy.trees[Config.geocode].root.hashcode}")

    # Size of full tree uncompressed received through join request
    Config.stats.record_stat(f"{Config.config["node_name"]}_received_tree_size", f"{asizeof.asizeof(received_tree)}")
    # Size of full tree compressed received through join request
    Config.stats.record_stat(f"{Config.config["node_name"]}_received_compressed_tree_size", f"{asizeof.asizeof(data)}")

    await asyncio.sleep(int(opts[-1]))
    return


async def update() -> None:
    """
    Start sync process by sending sync notifications to other nodes. Root hash of current state of tree is used.
    """

    logging.info("Sending notification interests")
    root_hash, seg_cnt, asset_name = Config.packed_updates_queue[-1]

    sync_requests = []
    Config.timer.start_global_timer(f"notification_interest")
    for route in Config.config["multi_cast_routes"]:
        sync_requests.append(send_sync_request(route, root_hash, asset_name, seg_cnt))
    await asyncio.gather(*sync_requests)

    return


async def wait(opts: Options) -> None:
    """
    Wait for specified time to allow other actions on this node or other nodes, interests will still be received and processed during waiting

    Args:
        opts: Action options:
                opts[0] = wait time
    """

    logging.info("Action: Waiting")
    await asyncio.sleep(int(opts[0]))
    return


async def serve_tree(opts: Options) -> None:
    """
    Prepare signed packets for tree and register route to enable receiving interests for tree

    Args:
        opts: Action options:
            opts[0] = geocode of tree to serve,
            opts[-1] = wait time after action
    """
    logging.info(f"Action: Serving tree with geocode {opts[0]}")

    Config.timer.start_timer(f"prep_tree")
    geocode_route = Config.config["direct_geocode_prefix"] + f"/{Config.geocode}"
    logging.info(f"Packing tree with geocode {Config.geocode}")
    serialized_data = pickle.dumps(Config.spasy.trees[Config.geocode])
    packets, seg_cnt = pack_data(serialized_data, geocode_route)
    Config.packed_tree_geocode = (packets, seg_cnt)

    await Config.app.register(geocode_route, on_direct_geocode_interest)
    logging.info(f"Registered route for {geocode_route}")
    Config.timer.stop_timer(f"prep_tree")

    # Number of packets
    Config.stats.record_stat(f"num_packets_tree", f"{seg_cnt}")

    await asyncio.sleep(int(opts[-1]))
    return


async def prep_queue(asset_name: str) -> None:
    """
    Prepare signed packets for recent updates queue for tree and register route to enable receiving interests for queue. Used after making a change to the tree.

    Args:
        asset_name: Name of asset associated with change
    """

    logging.info(f"Packing queue with hashcode {Config.spasy.trees[Config.geocode].root.hashcode} with asset {asset_name}")

    Config.timer.start_timer(f"prep_queue")

    # Pack recent updates
    root_hash_route = Config.config["direct_root_hash_prefix"] + f"/{Config.spasy.trees[Config.geocode].root.hashcode}"
    serialized_data = pickle.dumps(Config.spasy.trees[Config.geocode].recent_updates)
    packets, seg_cnt = pack_data(serialized_data, root_hash_route)

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


async def prep_asset(asset_name: str, asset_path: str) -> None:
    """
    Prepare signed packets for an asset and register route to enable receiving interests for asset

    Args:
        asset_name: Name of asset
        asset_path: Location of asset on disk
    """

    Config.timer.start_timer("prep_asset")
    asset_route = Config.config["direct_asset_prefix"] + asset_name
    logging.info(f"Packing asset with name {asset_route}")

    with open(asset_path, 'rb') as asset_file:
        data = asset_file.read()
    packets, seg_cnt = pack_data(data, asset_route)
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
    "WAIT": wait,
    "SERVE_TREE": serve_tree,
}
