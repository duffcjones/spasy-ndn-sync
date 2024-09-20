from ndn.types import InterestNack, InterestTimeout, InterestCanceled, ValidationFailure
from ndn.encoding import Name, Component

import logging
import pickle
import asyncio

import Config

async def send_interest(name):
    data_name, meta_info, data = None, None, None
    try:
        logging.info(f"Sending interest for {name}")
        data_name, meta_info, data = await Config.app.express_interest(
            Name.normalize(name), must_be_fresh=True, can_be_prefix=True,
            lifetime=100)
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
        logging.info(f'Received response for {Name.to_str(name)}')
        return data_name, meta_info, data


async def send_init_interests():
    for route in Config.config["routes"]:
        name = route + Config.config["initialization_postfix"]
        await send_interest(name)


async def send_root_request(name):
    num_seg, data = await fetch_segments(name)
    received_tree = pickle.loads(data)
    logging.info("Received tree")
    return received_tree

async def fetch_segments(name):
    segments = []
    logging.info(f"Sending initial interest for root {name}")
    data_name, meta_info, seg = await send_interest(Name.normalize(name) + [Component.from_segment(0)])
    segments.append((data_name, meta_info, seg))

    root_requests = []
    current_seg = 1
    while current_seg < 100:
        logging.info(f"Requesting segment {current_seg}")
        root_requests.append(send_interest(Name.normalize(name) + [Component.from_segment(current_seg)]))
        if meta_info.final_block_id == Component.from_segment(current_seg):
            break
        current_seg += 1
    segments.extend(await asyncio.gather(*root_requests))

    data = b''
    for _, _, segment in segments:
        data += bytes(segment)

    return current_seg, data


async def send_sync_request(route, root_hash):
    name = route + Config.config["multi_postfix"] + Config.config["direct_prefix"] + root_hash
    await send_interest(name)
