from ndn.app import NDNApp
from ndn.encoding import Name, InterestParam, BinaryStr, FormalName, MetaInfo
from ndn.types import InterestNack, InterestTimeout, InterestCanceled, ValidationFailure

from typing import Optional
import logging
import argparse
import json
import asyncio
from collections import deque
import pickle

from Spasy import Spasy
from ndn.encoding import Name, Component
import time
from Timer import Timer

app = NDNApp()

content = "received".encode()
root_geocode = ''
spasy = Spasy("DPWHWT")
config = {}
actions = []
packed_trees = {}
requests = deque()
timer = Timer()


async def main():
    logging.info("Registering prefixes")

    if actions[1].split(" ")[0] == "UPDATE":
        await app.register(config["direct_prefix"], on_direct_interest)
    else:
        await app.register(config["initialization_prefix"], on_init_interest)
        await app.register(config["multi_prefix"], on_multi_interest)

    time.sleep(config["init_time"])

    if actions[1].split(" ")[0] == "UPDATE":
        for route in config["routes"]:
            await send_init_interest(route)

        time.sleep(config["init_time"])
        await run_actions()


async def send_init_interest(route):
    name = route + config["initialization_postfix"]
    logging.info(f"Send init interest to {name}")
    data_name, meta_info, seg = await app.express_interest(
        Name.normalize(name), must_be_fresh=True, can_be_prefix=True,
        lifetime=100)
    logging.info("Received init interest")


async def send_root_request(name):
    received_tree = None
    try:
        data = b''
        seg_no = 0
        num_seg, data = await fetch_segments(name)
        received_tree = pickle.loads(data)
    except InterestNack as e:
        logging.info(f'Nacked with reason={e.reason}')
    except InterestTimeout:
        logging.info(f'Timeout')
    except InterestCanceled:
        logging.info(f'Canceled')
    except ValidationFailure:
        logging.info(f'Data failed to validate')
    except Exception as e:
        logging.info(f'Error: {e}')
    finally:
        return received_tree


async def fetch_segments(name):
    data = b''
    seg_no = 0
    while seg_no < 100:
        data_name, meta_info, seg = await app.express_interest(
            Name.normalize(name) + [Component.from_segment(seg_no)], must_be_fresh=True, can_be_prefix=True,
            lifetime=100)

        data += bytes(seg)
        if meta_info.final_block_id == Component.from_segment(seg_no):
            break
        else:
            seg_no += 1

    return seg_no, data


def setup(config_file, actions_file):
    global config
    with open(config_file, mode="r") as file:
        config = json.load(file)

    logging.basicConfig(
        filemode='a',
        format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
        datefmt='%H:%M:%S',
        level=config["log_level"])

    global root_geocode
    root_geocode = config["root_geocode"]

    global spasy
    spasy = Spasy(root_geocode)

    global actions
    with open(actions_file, mode="r") as file:
        actions = file.read().splitlines()
        logging.debug(actions)


async def run_actions():
    for action in actions:
        if action.split(" ")[0] == "UPDATE":
            serialized_tree = pickle.dumps(spasy)
            pack_tree(serialized_tree, spasy.tree.root.hashcode)
            logging.info(f'Adding data at geocode DPWHWTSH401')

            sync_requests = []
            for route in config["routes"]:
                task = asyncio.create_task(send_sync_request(route, spasy.tree.root.hashcode))
                sync_requests.append(task)


async def send_sync_request(route, root_hash):
    name = route + config["multi_postfix"] + config["direct_prefix"] + root_hash

    try:
        logging.info(f'Sending Sync Interest {name}')
        data_name, meta_info, response = await app.express_interest(
            Name.normalize(name), must_be_fresh=True, can_be_prefix=True, lifetime=100)
        logging.info(f'Received Sync Interest {data_name}')
    except InterestCanceled:
        logging.debug(f'Canceled')
    except ValidationFailure:
        logging.debug(f'Data failed to validate')
    except InterestNack:
        logging.debug(f'Sync request sent')
    except InterestTimeout:
        logging.debug(f'Sync request sent')
    finally:
        pass


def on_multi_interest(name: FormalName, param: InterestParam, app_param: Optional[BinaryStr]):
    logging.info(f'>> Multi Interest: {Name.to_str(name)}')
    global content
    app.put_data(name, content=content, freshness_period=100)
    logging.info(f'<< Data: {name}')
    name = Name.to_str(name)
    sender = "/" + name.split("//")[-1].rsplit("/", 1)[0]
    root_hash = name.split("/")[-1]
    logging.info(f'Received Root Hash {root_hash} from {sender}')
    asyncio.create_task(receive_hash(root_hash,sender))


def on_direct_interest(name, param, app_param):
    logging.info(f'>> Direct Interest: {Name.to_str(name)}, {param}')
    logging.info(f'<< Data: {Name.to_str(name)}')

    packets, seg_cnt = packed_trees[Name.to_str(name).rsplit("/",1)[0]]
    seg_no = Component.to_number(name[-1])

    if seg_no < seg_cnt:
        app.put_raw_packet(packets[Component.to_number(name[-1])])


def on_init_interest(name, param, app_param):
    logging.info(f'>> Interest: {Name.to_str(name)}, {param}')
    logging.info(f'<< Data: {Name.to_str(name)}')
    app.put_data(name, content=content, freshness_period=100)


async def receive_hash(root_hash, sender):
    name = sender + "/" + root_hash
    logging.info(f'Sending Root Request {name}')
    received_tree = await send_root_request(name)
    logging.info(f'Received Root Request {type(received_tree)}')
    logging.info(f'Updated tree with hash')


def pack_tree(serialized_tree, root_hash):
    seg_cnt = (len(serialized_tree) + config["packet_segment_size"] - 1) // config["packet_segment_size"]
    name = config["direct_prefix"] + root_hash

    global app
    packets = [app.prepare_data(Name.normalize(name) + [Component.from_segment(i)],
                                serialized_tree[i * config["packet_segment_size"]:(i + 1) * config["packet_segment_size"]],
                                freshness_period=10000,
                                final_block_id=Component.from_segment(seg_cnt - 1),
                                no_signature=True)
               for i in range(seg_cnt)]

    logging.info(f'Created {seg_cnt} chunks under name {name} ')

    global packed_trees
    packed_trees[Name.to_str(name)] = (packets, seg_cnt)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("config_file")
    parser.add_argument('--actions', dest='actions_file')
    args = parser.parse_args()
    setup(args.config_file, args.actions_file)
    app.run_forever(after_start=main())
