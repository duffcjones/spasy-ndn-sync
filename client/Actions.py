import logging
import asyncio
import pickle

import Config
from Interests import send_init_interests, send_sync_request
from Util import pack_tree
from Spasy import Spasy
from Callbacks import on_direct_interest


async def init(opts):
    logging.info(f'Action: Init with geocode {opts[0]}')
    Config.spasy = Spasy(opts[0])
    logging.info(Config.spasy.tree.root.hashcode)
    return


async def add(opts):
    logging.info(f"Action: Add data {opts[0]}")
    Config.spasy.add_data_to_tree(opts[0])
    return


async def join(opts):
    logging.info(f"Action: Join geocode {opts[0]}")
    return


async def update(opts):
    logging.info("Action: Update")

    logging.info(f"Registering route for {Config.config["direct_prefix"] + "/" + Config.spasy.tree.root.hashcode}")
    await Config.app.register(Config.config["direct_prefix"] + f"/{Config.spasy.tree.root.hashcode}", on_direct_interest)

    logging.info("Packing tree")
    serialized_tree = pickle.dumps(Config.spasy)
    seg_cnt = pack_tree(serialized_tree, Config.spasy.tree.root.hashcode)

    sync_requests = []
    for route in Config.config["routes"]:
        task = asyncio.create_task(send_sync_request(route, Config.spasy.tree.root.hashcode, seg_cnt))
        # await asyncio.sleep(0)
        sync_requests.append(task)
    return


async def wait(opts):
    logging.info("Action: Waiting")
    await asyncio.sleep(Config.config["wait_time"])
    return

actions = {
    "INIT": init,
    "ADD": add,
    "JOIN": join,
    "UPDATE": update,
    "WAIT": wait
}
