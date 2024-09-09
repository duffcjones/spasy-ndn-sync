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
    logging.debug(f'Registering prefix {config["node_name"]}')
    await app.register(config["direct_prefix"], on_direct_interest)
    await app.register(config["multi_prefix"], on_multi_interest)

    logging.debug(f'Initial tree root hash: {spasy.tree.root.hashcode}')

    requests_thread = threading.Thread(target=run_actions, daemon=True)
    requests_thread.start()

    send_root_requests()

    # requests_thread = threading.Thread(target=send_root_requests, daemon=True)
    # requests_thread.start()



    # for action in actions:
    #     if action.split(" ")[0] == "UPDATE":
    #         logging.info(f'Adding data at geocode DPWHWTSH401')
    #         # timer.start_timer("Add Data")
    #         # spasy.add_data_to_tree('/add/data/DPWHWTSH401')
    #         # timer.stop_timer("Add Data")
    #         logging.debug(f'Tree root hash {spasy.tree.root.hashcode}')
    #         # timer.start_timer("Serialize tree")
    #         serialized_tree = pickle.dumps(spasy)
    #         # timer.stop_timer("Serialize tree")
    #
    #         pack_tree(serialized_tree, spasy.tree.root.hashcode)
    #
    #         # timer.start_timer("Sync request")
    #         await send_sync_requests(spasy.tree.root.hashcode)
    #         # timer.stop_timer("Sync request")
    #
    #     await asyncio.sleep(config["wait_time"])

    # timer.dump()

    # await asyncio.sleep(10)
    # app.shutdown()

def run_actions():
    serialized_tree = pickle.dumps(spasy)
    pack_tree(serialized_tree, spasy.tree.root.hashcode)
    asyncio.run(run_action())
    # run_action()
    # for action in actions:
    #     if action.split(" ")[0] == "UPDATE":
    #         logging.info(f'Adding data at geocode DPWHWTSH401')
    #         # timer.start_timer("Add Data")
    #         # spasy.add_data_to_tree('/add/data/DPWHWTSH401')
    #         # timer.stop_timer("Add Data")
    #         logging.debug(f'Tree root hash {spasy.tree.root.hashcode}')
    #         # timer.start_timer("Serialize tree")
    #         serialized_tree = pickle.dumps(spasy)
    #         # timer.stop_timer("Serialize tree")
    #
    #         pack_tree(serialized_tree, spasy.tree.root.hashcode)
    #
    #         # timer.start_timer("Sync request")
    #         await send_sync_requests(spasy.tree.root.hashcode)
    #         # timer.stop_timer("Sync request")
    #
    #     await asyncio.sleep(config["wait_time"])

async def run_action():
    for action in actions:
        if action.split(" ")[0] == "UPDATE":
            logging.info(f'Adding data at geocode DPWHWTSH401')
            # timer.start_timer("Add Data")
            # spasy.add_data_to_tree('/add/data/DPWHWTSH401')
            # timer.stop_timer("Add Data")
            logging.debug(f'Tree root hash {spasy.tree.root.hashcode}')
            # timer.start_timer("Serialize tree")
            serialized_tree = pickle.dumps(spasy)
            # timer.stop_timer("Serialize tree")

            pack_tree(serialized_tree, spasy.tree.root.hashcode)

            # timer.start_timer("Sync request")
            await send_sync_requests(spasy.tree.root.hashcode)
            # timer.stop_timer("Sync request")

        await asyncio.sleep(config["wait_time"])

def setup(config_file, actions_file):
    global config
    with open(config_file, mode="r", encoding="utf-8") as file:
        config = json.load(file)

    global root_geocode
    root_geocode = config["root_geocode"]

    global spasy
    spasy = Spasy(root_geocode)

    # global packed_trees
    # serialized_tree = pickle.dumps(spasy)
    # pack_tree(serialized_tree, spasy.tree.root.hashcode)

    global actions
    with open(actions_file, mode="r", encoding="utf-8") as file:
        actions = file.read().splitlines()
        logging.debug(actions)


def on_direct_interest(name, param, app_param):
    timer.start_timer("raw packet")
    logging.debug(f'>> Direct Interest: {Name.to_str(name)}, {param}')
    logging.debug(f'<< Data: {Name.to_str(name)}')

    packets, seg_cnt = packed_trees[Name.to_str(name).rsplit("/",1)[0]]
    seg_no = Component.to_number(name[-1])

    if seg_no < seg_cnt:
        app.put_raw_packet(packets[Component.to_number(name[-1])])

    timer.stop_timer("raw packet")
    timer.dump()


def on_multi_interest(name: FormalName, param: InterestParam, app_param: Optional[BinaryStr]):
    logging.info(f'>> Multi Interest: {name}, {param}')
    name = Name.to_str(name)
    # app.put_data(name, content="received".encode(), freshness_period=10000)
    # logging.debug(f'<< Data: {name}')
    # logging.debug(MetaInfo(freshness_period=10000))

    sender = "/" + name.split("//")[-1].rsplit("/", 1)[0]
    root_hash = name.split("/")[-1]
    logging.debug(f'Received Root Hash {root_hash} from {sender}')
    receive_hash(root_hash, sender)


# def on_chunk_interest(int_name, _int_param, _app_param):
#     logging.debug(f'>> Chunk Interest: {Name.to_str(int_name)}, {_int_param}')
#     if Component.get_type(int_name[-1]) == Component.TYPE_SEGMENT:
#         seg_no = Component.to_number(int_name[-1])
#     else:
#         seg_no = 0
#     if seg_no < seg_cnt:
#         app.put_raw_packet(packets[seg_no])


# def on_interest(name: FormalName, param: InterestParam, app_param: Optional[BinaryStr]):
#     logging.debug(f'>> Interest: {Name.to_str(name)}, {param}')
#     app.put_data(name, content=content.encode(), freshness_period=10000)
#     logging.debug(f'<< Data: {Name.to_str(name)}')
#     logging.debug(MetaInfo(freshness_period=10000))
#     logging.debug(f'Content: (size: {len(content)})')


async def send_sync_requests(root_hash):
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


def send_root_requests():
    global requests

    while True:
        if requests:
            name = "/spasy/h2/direct/e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
            requests.popleft()
            logging.debug(f'Sending Root Request {name}')
            received_tree = asyncio.run(send_root_request(name))
            logging.info(f'Updated tree with hash {spasy.tree.root.hashcode}')
            # spasy.replace_tree(received_tree)
            timer.dump()


async def send_root_request(name):
    received_tree = None
    try:
        logging.debug(f'Sending Root Interest {name}, {InterestParam(must_be_fresh=True, lifetime=6000)}')
        data = b''
        seg_no = 0
        # while True:
        logging.debug(seg_no)
        timer.start_timer("send_interest")
        data_name, meta_info, seg = await app.express_interest(
            Name.normalize(name) + [Component.from_segment(seg_no)], must_be_fresh=True, can_be_prefix=True,
            lifetime=100)
        timer.stop_timer("send_interest")
        # cnt, data, time_taken = await fetch_segments(name)

        # logging.debug(f'\n{cnt + 1} segments fetched.')
        logging.debug(f'Received Tree Name: {Name.to_str(name)}')
        received_tree = pickle.loads(data)
        logging.debug(sys.getsizeof(received_tree))
    except InterestCanceled:
        logging.debug(f'Canceled')
    except ValidationFailure:
        logging.debug(f'Data failed to validate')
    except InterestNack:
        logging.debug(f'Cancelled')
    except InterestTimeout:
        logging.debug(f'Data failed to validate')
    except Exception as e:
        logging.debug(f'Error: {e}')
    finally:
        return received_tree


def receive_hash(root_hash, sender):
    name = sender + "/" + root_hash

    global requests
    requests.append(name)
    logging.debug(f'Logging Hash: {name}')


def pack_tree(serialized_tree, root_hash):
    seg_cnt = (len(serialized_tree) + config["packet_segment_size"] - 1) // config["packet_segment_size"]
    name = config["direct_prefix"] + root_hash

    # 120 ms to prepare data
    global app
    packets = [app.prepare_data(Name.normalize(name) + [Component.from_segment(i)],
                                serialized_tree[i * config["packet_segment_size"]:(i + 1) * config["packet_segment_size"]],
                                freshness_period=10000,
                                final_block_id=Component.from_segment(seg_cnt - 1))
               for i in range(seg_cnt)]

    logging.info(f'Created {seg_cnt} chunks under name {name} ')
    logging.debug(f'{len(packets)}')

    global packed_trees
    packed_trees[Name.to_str(name)] = (packets, seg_cnt)


async def fetch_segments(name):
    data = b''
    seg_no = 0
    # while True:
    logging.debug(seg_no)
    timer.start_timer("send_interest")
    data_name, meta_info, seg = await app.express_interest(
        Name.normalize(name) + [Component.from_segment(seg_no)], must_be_fresh=True, can_be_prefix=True,
        lifetime=100)
    timer.stop_timer("send_interest")

    # data += bytes(seg)
    # if meta_info.final_block_id == Component.from_segment(seg_no):
    #     break
    # else:
    #     seg_no += 1

    return seg_no, data, 0


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("config_file")
    parser.add_argument('--actions', dest='actions_file')
    args = parser.parse_args()
    app = NDNApp()
    setup(args.config_file, args.actions_file)

    app.run_forever(after_start=main())
