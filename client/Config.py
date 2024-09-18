import json
import logging
from ndn.app import NDNApp

from Spasy import Spasy

app = NDNApp()
config = {}
spasy = Spasy("")
packed_trees = {}

def setup(config_file, actions_file):
    global config
    with open(config_file, mode="r") as file:
        config = json.load(file)

    logging.basicConfig(
        filemode='a',
        format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
        datefmt='%H:%M:%S',
        level=config["log_level"])

    global spasy
    spasy = Spasy(config["root_geocode"])

    with open(actions_file, mode="r") as file:
        actions = file.read().splitlines()

    return actions
