import logging
import asyncio
import pickle
import time

import Config
from Interests import send_init_interests, send_sync_request
from Util import pack_tree

async def update(opts):
    logging.info("Action: Update")

    logging.info("Packing tree")
    serialized_tree = pickle.dumps(Config.spasy)
    pack_tree(serialized_tree, Config.spasy.tree.root.hashcode)

    sync_requests = []
    for route in Config.config["routes"]:
        task = asyncio.create_task(send_sync_request(route, Config.spasy.tree.root.hashcode))
        sync_requests.append(task)


async def wait(opts):
    logging.info("Waiting")
    await asyncio.sleep(Config.config["wait_time"])

actions = {
    "UPDATE": update,
    "WAIT": wait
}
