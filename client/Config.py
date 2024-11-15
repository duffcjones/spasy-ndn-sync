import json
import logging
from collections import deque

from ndn.app import NDNApp
from ndn.security.keychain.keychain_digest import KeychainDigest

from Spasy import Spasy
from Timer import Timer
from Stats import Stats

app = None

config = {}
spasy = Spasy("")
geocode = ""

packed_updates_dict = {}
packed_updates_queue = deque()
packed_tree_geocode = None
packed_assets_dict = {}

timer = None
stats = None


def setup(config_file, actions_file):
    global config
    with open(config_file, mode="r") as file:
        config = json.load(file)

    global app
    if config["use_keychain_digest"]:
        app = NDNApp(keychain=KeychainDigest())
    else:
        app = NDNApp()

    logging.basicConfig(
        filemode='a',
        format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
        datefmt='%H:%M:%S',
        level=config["log_level"])

    global timer
    timer = Timer(config["timer_output_path"])
    global stats
    stats = Stats(config["stats_output_path"])

    with open(actions_file, mode="r") as file:
        actions = file.read().splitlines()

    return actions
