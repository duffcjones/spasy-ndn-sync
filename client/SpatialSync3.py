import logging
import argparse
import time
import asyncio

import Config
from Callbacks import on_multi_interest, on_init_interest
import Actions
from Interests import send_init_interests

async def main():
    # Config.timer.start_timer(f"{Config.config["node_name"]}_initialization_prefix_route_registration")
    await Config.app.register(Config.config["initialization_prefix"], on_init_interest)
    # Config.timer.stop_timer(f"{Config.config["node_name"]}_initialization_prefix_route_registration")
    logging.info(f"Registered prefix {Config.config["initialization_prefix"]}")

    # Config.timer.start_timer(f"{Config.config["node_name"]}_multi_prefix_route_registration")
    await Config.app.register(Config.config["multi_prefix"], on_multi_interest)
    # Config.timer.stop_timer(f"{Config.config["node_name"]}_multi_prefix_route_registration")
    logging.info(f"Registered prefix {Config.config["multi_prefix"]}")

    time.sleep(Config.config["init_time"])

    logging.info("Initializing interests")
    await send_init_interests()

    await asyncio.sleep(Config.config["init_time"])

    for action_key in action_list:
        action_params = action_key.split(" ")
        cmd = action_params[0]
        opts = action_params[1:]
        action = Actions.actions[cmd]
        await action(opts)

    Config.timer.dump()
    Config.stats.dump()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("config_file")
    parser.add_argument('--actions', dest='actions_file')
    args = parser.parse_args()

    action_list = Config.setup(args.config_file, args.actions_file)

    Config.app.run_forever(after_start=main())
