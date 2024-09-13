from ndn.app import NDNApp
from ndn.encoding import Name, InterestParam, BinaryStr, FormalName, MetaInfo
from ndn.types import InterestNack, InterestTimeout, InterestCanceled, ValidationFailure
from typing import Optional

import logging
import argparse
from Spasy import Spasy
import pickle
from ndn.encoding import Component

logging.basicConfig(
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.DEBUG)

content="hi"
spasy = Spasy("DPWHWT")
serialized_tree = None
packet = []


async def main(prefix):
    global serialized_tree
    serialized_tree = pickle.dumps(spasy)
    seg_cnt = (len(serialized_tree) + 1024 - 1) // 1024
    global packet
    packet = [app.prepare_data(Name.normalize(prefix) + [Component.from_segment(i)],
                     serialized_tree[i * 1024:(i + 1) * 1024],
                     freshness_period=10000,
                     final_block_id=Component.from_segment(seg_cnt - 1)) for i in range(seg_cnt)]
    await app.register(prefix, on_interest)
    # await app.register("/spasy/h1/multi", on_multi_interest)

def on_interest(name: FormalName, param: InterestParam, app_param: Optional[BinaryStr]):
    logging.debug(f'>> Interest: {Name.to_str(name)}, {param}')
    app.put_raw_packet(packet[0])
    # app.put_data(name, content=serialized_tree, freshness_period=10000)
    logging.debug(f'<< Data: {Name.to_str(name)}')
    # logging.debug(MetaInfo(freshness_period=10000))
    # logging.debug(f'Content: (size: {len(content)})')

# def on_multi_interest(name: FormalName, param: InterestParam, app_param: Optional[BinaryStr]):
#     logging.info(f'>> Multi Interest: {name}, {param}')
#     name = Name.to_str(name)
#     # app.put_data(name, content="received".encode(), freshness_period=10000)
#     # logging.debug(f'<< Data: {name}')
#     # logging.debug(MetaInfo(freshness_period=10000))
#
#     sender = "/" + name.split("//")[-1].rsplit("/", 1)[0]
#     root_hash = name.split("/")[-1]
#     logging.debug(f'Received Root Hash {root_hash} from {sender}')
#     # receive_hash(root_hash, sender)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("prefix")
    args = parser.parse_args()
    app = NDNApp()
    app.run_forever(after_start=main(args.prefix))
