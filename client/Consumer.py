from ndn.app import NDNApp
from ndn.encoding import Name, InterestParam, BinaryStr, FormalName, MetaInfo, Component
from ndn.types import InterestNack, InterestTimeout, InterestCanceled, ValidationFailure
from typing import Optional

import logging
import argparse

import time
from ndn.app_support.segment_fetcher import segment_fetcher
import pickle
from Timer import Timer
import asyncio
import threading
from Spasy import Spasy


logging.basicConfig(
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.DEBUG)

timer = Timer()
name = ""
content="hi"
spasy = Spasy("DPWHWT")
serialized_tree = None
packet = []


async def main(prefix):
    global name
    name = prefix
    # await app.register("/spasy/h3/multi", on_multi_interest)

    time.sleep(3)

    # try:
    #     cnt = 0
    #     data = b''
    #     async for seg in segment_fetcher(app, prefix):
    #         data += bytes(seg)
    #         cnt += 1
    #     logging.info(pickle.loads(data))
    #     logging.info(f'\n{cnt} segments fetched.')
    # try:
    #     logging.info("Sending interest")
    #     timer.start_timer("test")
    #     data_name, meta_info, seg = await app.express_interest(
    #         Name.normalize(prefix) + [Component.from_segment(0)], must_be_fresh=True, can_be_prefix=True,
    #         lifetime=100)
    #     timer.stop_timer("test")
    #     logging.info("Received interest")
    #     logging.info(bytes(seg))
    #     timer.dump()
    # except InterestNack as e:
    #     logging.info(f'Nacked with reason={e.reason}')
    # except InterestTimeout:
    #     logging.info(f'Timeout')
    # except InterestCanceled:
    #     logging.info(f'Canceled')
    # except ValidationFailure:
    #     logging.info(f'Data failed to validate')
    # finally:
    #     app.shutdown()

    global serialized_tree
    serialized_tree = pickle.dumps(spasy)
    seg_cnt = (len(serialized_tree) + 1024 - 1) // 1024
    global packet
    packet = [app.prepare_data(Name.normalize(prefix) + [Component.from_segment(i)],
                               serialized_tree[i * 1024:(i + 1) * 1024],
                               freshness_period=10000,
                               final_block_id=Component.from_segment(seg_cnt - 1)) for i in range(seg_cnt)]
    logging.info(f'Adding data at geocode DPWHWTSH401')
    routes = [""]
    sync_requests = []
    for route in routes:
        sync_requests.append(send_sync_request(route))
    await asyncio.gather(*sync_requests)

async def send_sync_request(name):
    try:
        logging.info(f'Sending Sync Interest {name}')
        data_name, meta_info, response = await app.express_interest(
            Name.normalize(name), must_be_fresh=True, can_be_prefix=True, lifetime=100)
        logging.info(f'Received Sync Response: {Name.to_str(data_name)}')
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

# def send_requests():
#     received_tree = asyncio.run(request(name))
#
# async def request(prefix):
#     try:
#         logging.info("Sending interest")
#         timer.start_timer("test")
#         data_name, meta_info, seg = await app.express_interest(
#             Name.normalize(prefix) + [Component.from_segment(0)], must_be_fresh=True, can_be_prefix=True,
#             lifetime=100)
#         timer.stop_timer("test")
#         logging.info("Received interest")
#         logging.info(bytes(seg))
#         timer.dump()
#     except InterestNack as e:
#         logging.info(f'Nacked with reason={e.reason}')
#     except InterestTimeout:
#         logging.info(f'Timeout')
#     except InterestCanceled:
#         logging.info(f'Canceled')
#     except ValidationFailure:
#         logging.info(f'Data failed to validate')

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
    # app.run_forever(after_start=main())
