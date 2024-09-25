import json
import logging
from collections import deque

from ndn.app import NDNApp

from Spasy import Spasy
from Timer import Timer

app = NDNApp()
config = {}
spasy = Spasy("")
geocode = ""

packed_trees_hashcode_dict = {}
packed_trees_queue = deque()

packed_tree_geocode = None

timer = None

def setup(config_file, actions_file):
    global config
    with open(config_file, mode="r") as file:
        config = json.load(file)

    logging.basicConfig(
        filemode='a',
        format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
        datefmt='%H:%M:%S',
        level=config["log_level"])

    with open(actions_file, mode="r") as file:
        actions = file.read().splitlines()

    global timer
    timer = Timer(config["output_path"])

    return actions
