import sys

from ndn.app import NDNApp
from ndn.encoding import Name, InterestParam, BinaryStr, FormalName, MetaInfo
from ndn.types import InterestNack, InterestTimeout, InterestCanceled, ValidationFailure

from typing import Optional
import logging
import argparse
import json
import asyncio
import threading
from collections import deque
import pickle

from Spasy import Spasy
from ndn.encoding import Name, Component
import time
from Timer import Timer

logging.basicConfig(
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.INFO)

root_geocode = ''
spasy = Spasy("DPWHWT")
config = {}
actions = []
packed_trees = {}
requests = deque()
timer = Timer()


async def main():
    logging.info("Registering prefixes")
    await app.register(config["multi_prefix"], on_multi_interest)
    await app.register(config["direct_prefix"], on_direct_interest)

    time.sleep(2)

    requests_thread = threading.Thread(target=run_actions, daemon=False)
    requests_thread.start()

    up_time = time.time()
    while time.time() - up_time < 10:
        await asyncio.sleep(0)
        if requests:
            name = requests.popleft()
            logging.info(f'Sending Root Request {name}')
            received_tree = await send_root_request(name)
            logging.info(f'Received Root Request {type(received_tree)}')
            global spasy
            spasy.replace_tree(received_tree)
            logging.info(f'Updated tree with hash {received_tree.tree.root.hashcode}')
            break
    timer.dump()
    app.shutdown()


async def send_root_request(name):
    received_tree = None
    try:
        logging.info(f'Sending Root Interest {name}, {InterestParam(must_be_fresh=True, lifetime=6000)}')
        data = b''
        seg_no = 0
        logging.debug(seg_no)
        timer.start_timer("send_interest")
        data_name, meta_info, seg = await app.express_interest(
            Name.normalize(name) + [Component.from_segment(seg_no)], must_be_fresh=True, can_be_prefix=True,
            lifetime=1000)
        timer.stop_timer("send_interest")
        data += bytes(seg)
        logging.info(f'Received Tree Name: {Name.to_str(name)}')
        received_tree = pickle.loads(data)
        logging.info(sys.getsizeof(received_tree))
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


def setup(config_file, actions_file):
    global config
    with open(config_file, mode="r", encoding="utf-8") as file:
        config = json.load(file)

    global root_geocode
    root_geocode = config["root_geocode"]

    global spasy
    spasy = Spasy(root_geocode)

    global actions
    with open(actions_file, mode="r", encoding="utf-8") as file:
        actions = file.read().splitlines()
        logging.debug(actions)


def run_actions():
    for action in actions:
        if action.split(" ")[0] == "UPDATE":
            logging.info(f'Adding data at geocode DPWHWTSH401')
            serialized_tree = pickle.dumps(spasy)
            pack_tree(serialized_tree, spasy.tree.root.hashcode)
            asyncio.run(send_sync_requests(spasy.tree.root.hashcode))


async def send_sync_requests(root_hash):
    logging.info("Loading sync requests")
    sync_requests = []
    for route in config["routes"]:
        sync_requests.append(send_sync_request(route, root_hash))
    await asyncio.gather(*sync_requests)


async def send_sync_request(route, root_hash):
    try:
        name = route + config["multi_postfix"] + config["direct_prefix"] + root_hash
        logging.info(f'Sending Sync Interest {name}')
        data_name, meta_info, response = await app.express_interest(
            Name.normalize(name), must_be_fresh=True, can_be_prefix=True, lifetime=1)
        logging.debug(f'Received Sync Interest {data_name}')
        logging.debug(f'Received Data Name: {Name.to_str(data_name)}')
        logging.debug(meta_info)
        logging.debug(bytes(response) if response else None)
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
    logging.info(f'>> Multi Interest: {name}, {param}')
    name = Name.to_str(name)
    sender = "/" + name.split("//")[-1].rsplit("/", 1)[0]
    root_hash = name.split("/")[-1]
    logging.debug(f'Received Root Hash {root_hash} from {sender}')
    receive_hash(root_hash, sender)


def on_direct_interest(name, param, app_param):
    logging.debug(f'>> Direct Interest: {Name.to_str(name)}, {param}')
    logging.debug(f'<< Data: {Name.to_str(name)}')

    packets, seg_cnt = packed_trees[Name.to_str(name).rsplit("/",1)[0]]
    seg_no = Component.to_number(name[-1])

    if seg_no < seg_cnt:
        app.put_raw_packet(packets[Component.to_number(name[-1])])


def receive_hash(root_hash, sender):
    name = sender + "/" + root_hash
    global requests
    requests.append(name)


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
    app = NDNApp()
    setup(args.config_file, args.actions_file)
    app.run_forever(after_start=main())
