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
from ndn.app_support.segment_fetcher import segment_fetcher

logging.basicConfig(
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.DEBUG)

root_geocode = ''
spasy = Spasy("ASDF")
config = {}
actions = []
packed_trees = {}
requests = deque()


async def main():
    # tree_file = pathlib.Path("/tmp/geohash_tree.pickle")
    # tree.unlink(missing_ok=True)

    # logging.info(tree)

    # with open('/tmp/geohash_tree.pickle', 'wb') as file:
    #     pickle.dump(geohash_tree, file, protocol=pickle.HIGHEST_PROTOCOL)
    #
    # with open('/tmp/geohash_tree.pickle', 'rb') as handle:
    #     b = pickle.load(handle)
    #     logging.info(type(b))
    #     logging.info(b)

    # name.append(Component.from_version(timestamp()))

    # data = packed_tree
    # global seg_cnt
    # seg_cnt = (len(data) + config["packet_segment_size"] - 1) // config["packet_segment_size"]
    # global packets
    # packets = [app.prepare_data(Name.normalize("/spasy/h0/direct/DPWHWT") + [Component.from_segment(i)],
    #                             data[i * config["packet_segment_size"]:(i + 1) * config["packet_segment_size"]],
    #                             freshness_period=10000,
    #                             final_block_id=Component.from_segment(seg_cnt - 1))
    #            for i in range(seg_cnt)]
    # logging.info(f'Created {seg_cnt} chunks under name {Name.to_str("/spasy/direct/DPWHWT")}')

    logging.info(f'Registering prefix {config["node_name"]}')
    await app.register(config["direct_prefix"], on_direct_interest)
    await app.register(config["multi_prefix"], on_multi_interest)

    requests_thread = threading.Thread(target=send_root_requests, daemon=True)
    requests_thread.start()

    for action in actions:
        if action.split(" ")[0] == "UPDATE":
            logging.info(f'Tree root hash {spasy.tree.root.hashcode}')
            logging.info(f'Adding data at geocode DPWHWTSH401')
            spasy.add_data_to_tree('DPWHWTSH401', '/add/data')
            logging.info(f'Tree root hash {spasy.tree.root.hashcode}')
            serialized_tree = pickle.dumps(spasy)
            pack_tree(serialized_tree, spasy.tree.root.hashcode)
            await send_sync_request(spasy.tree.root.hashcode)
            # await asyncio.sleep(int(action.split(" ")[-1]))
        await asyncio.sleep(config["wait_time"])

    # await asyncio.sleep(10)
    # app.shutdown()


def setup(config_file, actions_file):
    global config
    with open(config_file, mode="r", encoding="utf-8") as file:
        config = json.load(file)

    global root_geocode
    root_geocode = config["root_geocode"]

    global spasy
    spasy = Spasy(root_geocode)

    global packed_trees
    serialized_tree = pickle.dumps(spasy)
    pack_tree(serialized_tree, spasy.tree.root.hashcode)

    global actions
    with open(actions_file, mode="r", encoding="utf-8") as file:
        actions = file.read().splitlines()
        logging.info(actions)


def on_direct_interest(name, param, app_param):
    logging.info(f'>> Direct Interest: {Name.to_str(name)}, {param}')
    logging.info(f'<< Data: {Name.to_str(name)}')
    logging.info(MetaInfo(freshness_period=10000))

    if Component.get_type(name[-1]) == Component.TYPE_SEGMENT:
        packets, seg_cnt = packed_trees[Name.to_str(name).rsplit("/",1)[0]]
        seg_no = Component.to_number(name[-1])
    else:
        packets, seg_cnt = packed_trees[Name.to_str(name)]
        seg_no = 0

    if seg_no < seg_cnt:
        app.put_raw_packet(packets[seg_no])


def on_multi_interest(name: FormalName, param: InterestParam, app_param: Optional[BinaryStr]):
    logging.info(f'>> Multi Interest: {Name.to_str(name)}, {param}')
    app.put_data(name, content="received".encode(), freshness_period=10000)
    logging.info(f'<< Data: {Name.to_str(name)}')
    logging.info(MetaInfo(freshness_period=10000))

    sender = "/" + Name.to_str(name).split("//")[-1].rsplit("/", 1)[0]
    logging.info(f'Received Root Hash: {sender}')
    root_hash = Name.to_str(name).split("/")[-1]
    logging.info(f'Received Root Hash: {root_hash}')

    receive_hash(root_hash, sender)


# def on_chunk_interest(int_name, _int_param, _app_param):
#     logging.info(f'>> Chunk Interest: {Name.to_str(int_name)}, {_int_param}')
#     if Component.get_type(int_name[-1]) == Component.TYPE_SEGMENT:
#         seg_no = Component.to_number(int_name[-1])
#     else:
#         seg_no = 0
#     if seg_no < seg_cnt:
#         app.put_raw_packet(packets[seg_no])


# def on_interest(name: FormalName, param: InterestParam, app_param: Optional[BinaryStr]):
#     logging.info(f'>> Interest: {Name.to_str(name)}, {param}')
#     app.put_data(name, content=content.encode(), freshness_period=10000)
#     logging.info(f'<< Data: {Name.to_str(name)}')
#     logging.info(MetaInfo(freshness_period=10000))
#     logging.info(f'Content: (size: {len(content)})')


async def send_sync_request(root_hash):
    for route in config["routes"]:
        try:
            name = Name.from_str(route + config["multi_postfix"] + config["direct_prefix"] + root_hash)
            logging.info(f'Sending Sync Interest {Name.to_str(name)}, {InterestParam(must_be_fresh=True, lifetime=6000)}')
            data_name, meta_info, response = await app.express_interest(
                name, must_be_fresh=True, can_be_prefix=True, lifetime=100)

            logging.info(f'Received Data Name: {Name.to_str(data_name)}')
            logging.info(meta_info)
            logging.info(bytes(response) if response else None)
        except InterestCanceled:
            logging.info(f'Canceled')
        except ValidationFailure:
            logging.info(f'Data failed to validate')
        except InterestNack:
            logging.info(f'Sync request sent')
        except InterestTimeout:
            logging.info(f'Sync request sent')
        finally:
            pass


def send_root_requests():
    global requests
    while True:
        if requests:
            logging.info(f'Sending Root Requests')
            name = Name.from_str(requests.popleft())
            received_tree = asyncio.run(send_root_request(name))
            logging.info(f'Updated tree with hash {spasy.tree.root.hashcode}')
            spasy.replace_tree(received_tree)


async def send_root_request(name):
    received_tree = None
    try:
        logging.info(f'Sending Root Interest {Name.to_str(name)}, {InterestParam(must_be_fresh=True, lifetime=6000)}')

        cnt = 0
        data = b''
        async for seg in segment_fetcher(app, name):
            data += bytes(seg)
            cnt += 1
        logging.info(f'\n{cnt} segments fetched.')
        logging.info(f'Received Tree Name: {Name.to_str(name)}')
        received_tree = pickle.loads(data)
        logging.info(sys.getsizeof(received_tree))
    except InterestCanceled:
        logging.info(f'Canceled')
    except ValidationFailure:
        logging.info(f'Data failed to validate')
    except InterestNack:
        logging.info(f'Cancelled')
    except InterestTimeout:
        logging.info(f'Data failed to validate')
    except Exception as e:
        logging.info(f'Error: {e}')
    finally:
        return received_tree


def receive_hash(root_hash, sender):
    name = sender + "/" + root_hash

    global requests
    requests.append(name)
    logging.info(f'Logging Hash: {name}')


def pack_tree(serialized_tree, root_hash):
    seg_cnt = (len(serialized_tree) + config["packet_segment_size"] - 1) // config["packet_segment_size"]
    name = Name.normalize(config["direct_prefix"] + root_hash)
    global app
    packets = [app.prepare_data(name + [Component.from_segment(i)],
                                serialized_tree[i * config["packet_segment_size"]:(i + 1) * config["packet_segment_size"]],
                                freshness_period=10000,
                                final_block_id=Component.from_segment(seg_cnt - 1))
               for i in range(seg_cnt)]
    logging.info(f'Created {seg_cnt} chunks under name {Name.to_str(name)}')

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
