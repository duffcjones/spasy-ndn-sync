import logging
import argparse
import asyncio
import pickle
import time

import Config
from Callbacks import on_direct_interest, on_multi_interest, on_init_interest
from Interests import send_init_interest, send_sync_request
from Util import pack_tree

async def main():
    if actions[1].split(" ")[0] == "UPDATE":
        await Config.app.register(Config.config["direct_prefix"], on_direct_interest)
    else:
        await Config.app.register(Config.config["initialization_prefix"], on_init_interest)
        await Config.app.register(Config.config["multi_prefix"], on_multi_interest)

    time.sleep(Config.config["init_time"])

    if actions[1].split(" ")[0] == "UPDATE":
        for route in Config.config["routes"]:
            await send_init_interest(route)

        time.sleep(Config.config["init_time"])
        await run_actions()


async def run_actions():
    for action in actions:
        if action.split(" ")[0] == "UPDATE":
            serialized_tree = pickle.dumps(Config.spasy)
            pack_tree(serialized_tree, Config.spasy.tree.root.hashcode)

            sync_requests = []
            for route in Config.config["routes"]:
                task = asyncio.create_task(send_sync_request(route, Config.spasy.tree.root.hashcode))
                sync_requests.append(task)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("config_file")
    parser.add_argument('--actions', dest='actions_file')
    args = parser.parse_args()

    actions = Config.setup(args.config_file, args.actions_file)

    Config.app.run_forever(after_start=main())
