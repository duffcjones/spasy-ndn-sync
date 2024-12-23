import logging
import argparse
import asyncio

import Config
import Actions
from Callbacks import on_multi_interest, on_init_interest


async def main() -> None:
    """
    Run actions given to node and dump timing results and statistics once finished
    """

    await Config.app.register(Config.config["initialization_prefix"], on_init_interest)
    logging.info(f"Registered prefix {Config.config["initialization_prefix"]}")

    await Config.app.register(Config.config["multi_prefix"], on_multi_interest)
    logging.info(f"Registered prefix {Config.config["multi_prefix"]}")

    await asyncio.sleep(1)

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
