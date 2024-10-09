from ndn.types import InterestNack, InterestTimeout, InterestCanceled, ValidationFailure
from ndn.encoding import Name, Component

import logging
import pickle
import asyncio

from pympler.asizeof import asizeof

import Config

async def send_interest(name):
    data_name, meta_info, data = None, None, None
    try:
        logging.info(f"Sending interest for {name}")
        data_name, meta_info, data = await Config.app.express_interest(
            Name.normalize(name), must_be_fresh=True, can_be_prefix=True,
            lifetime=100)
        logging.info(f'Received response for {Name.to_str(data_name)}')
        logging.info(f"data_name: {asizeof(data_name)}")
        logging.info(f"meta_info: {asizeof(meta_info)}")
        logging.info(f"data: {asizeof(data)}")
    except InterestNack as e:
        logging.info(f'Interest {name} nacked with reason={e.reason}')
    except InterestTimeout:
        logging.info(f'Interest {name} timed out')
    except InterestCanceled:
        logging.info(f'Interest {name} canceled')
    except ValidationFailure:
        logging.info(f'Interest {name} data failed to validate')
    except Exception as e:
        logging.info(f'Interest {name} error: {e}')
    finally:
        return data_name, meta_info, data


async def send_init_interests():
    for route in Config.config["multi_cast_routes"]:
        name = route + Config.config["initialization_path"]
        Config.timer.start_timer(f"{Config.config["node_name"]}_init_interest")
        await send_interest(name)
        Config.timer.stop_timer(f"{Config.config["node_name"]}_init_interest")
    return


async def send_root_request(name, seg_cnt):
    num_seg, received_tree, data = await fetch_segments_concurrent(name, seg_cnt)
    logging.info(f"Received response for interest {name}")
    return received_tree, data


async def fetch_segments(name):
    segments = []
    current_seg = 0
    logging.info(f"Sending initial interest for tree with root {name}")
    # Config.timer.start_timer(f"{Config.config["node_name"]}_")
    data_name, meta_info, seg = await send_interest(Name.normalize(name) + [Component.from_segment(current_seg)])
    segments.append((data_name, meta_info, seg))

    if meta_info.final_block_id != Component.from_segment(0):
        root_requests = []
        current_seg = 1
        while current_seg < 1000:
            logging.info(f"Requesting segment {current_seg} of tree with root {name}")
            root_requests.append(send_interest(Name.normalize(name) + [Component.from_segment(current_seg)]))
            if meta_info.final_block_id == Component.from_segment(current_seg):
                break
            current_seg += 1
        segments.extend(await asyncio.gather(*root_requests))

    data = b''
    for _, _, segment in segments:
        data += bytes(segment)

    received_tree = pickle.loads(data)
    # received_tree = data
    # logging.info(f"Type is {type(received_tree)}")

    return current_seg, received_tree, data


async def fetch_segments_concurrent(name, seg_cnt):
    segments = []
    logging.info(f"Sending interests for root {name}")

    root_requests = []
    for current_seg in range(int(seg_cnt)):
        logging.info(f"Requesting segment {current_seg} of tree with root {name}")
        root_requests.append(send_interest(Name.normalize(name) + [Component.from_segment(current_seg)]))
    segments.extend(await asyncio.gather(*root_requests))

    data = b''
    for _, _, segment in segments:
        data += bytes(segment)

    received_tree = pickle.loads(data)
    return seg_cnt, received_tree, data


async def fetch_segments_sequential(name):
    segments = []
    current_seg = 0
    logging.info(f"Sending interests for tree with root {name}")
    data = b''
    root_requests = []
    current_seg = 0
    while current_seg < 1000:
        logging.info(f"Requesting segment {current_seg} of tree with root {name}")
        data_name, meta_info, seg = await send_interest(Name.normalize(name) + [Component.from_segment(current_seg)])
        data += bytes(seg)
        if meta_info.final_block_id == Component.from_segment(current_seg):
            break
        current_seg += 1
    received_tree = pickle.loads(data)
    return current_seg, received_tree, data


async def send_sync_request(route, root_hash, seg_cnt):
    name = route + Config.config["multi_path"] + f"/{root_hash}" + f"/{Config.geocode}" + f"/{seg_cnt}"
    await send_interest(name)
    return
