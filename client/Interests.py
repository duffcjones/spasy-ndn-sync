from ndn.types import InterestNack, InterestTimeout, InterestCanceled, ValidationFailure
from ndn.encoding import Name, Component

import logging
import pickle
import asyncio

import Config

async def send_interest(name, ttl=5000):
    data_name, meta_info, data = None, None, None
    try:
        logging.info(f"Sending interest for {name}")
        data_name, meta_info, data = await Config.app.express_interest(
            Name.normalize(name),must_be_fresh=False, can_be_prefix=True,
            lifetime=ttl)
        logging.info(f'Received response for {Name.to_str(data_name)}')
    except InterestNack as e:
        logging.info(f'Interest {name} nacked with reason={e.reason}')
    except InterestTimeout as e:
        logging.info(f'Interest {name} timed out')
    except InterestCanceled as e:
        logging.info(f'Interest {name} canceled')
    except ValidationFailure as e:
        logging.info(f'Interest {name} data failed to validate with reason={e.result}')
    except Exception as e:
        logging.info(f'Interest {name} error: {e}')
    finally:
        return data_name, meta_info, data


async def send_init_interests():
    for route in Config.config["multi_cast_routes"]:
        name = route + Config.config["initialization_path"]
        await send_interest(name)
    return


async def send_root_request(name, seg_cnt):
    data, num_seg = await fetch_segments_concurrent(name, seg_cnt)
    received_update = pickle.loads(data)
    logging.info(f"Received response for interest {name}")
    return received_update, num_seg, data


async def send_asset_request(name):
    data, num_seg = await fetch_segments_batch(name,Config.config["batch_size"])
    return data, num_seg


async def fetch_segments(name):
    segments = []
    current_seg = 0
    logging.info(f"Sending initial interest for tree with root {name}")
    data_name, meta_info, seg = await send_interest(Name.normalize(name) + [Component.from_segment(current_seg)])
    segments.append((data_name, meta_info, seg))

    if meta_info.final_block_id != Component.from_segment(0):
        seg_requests = []
        current_seg = 1
        while current_seg < Config.config["max_packets"]:
            logging.info(f"Requesting segment {current_seg} of tree with root {name}")
            seg_requests.append(send_interest(Name.normalize(name) + [Component.from_segment(current_seg)]))
            if meta_info.final_block_id == Component.from_segment(current_seg):
                break
            current_seg += 1
        segments.extend(await asyncio.gather(*seg_requests))

    data = b''
    for _, _, segment in segments:
        data += bytes(segment)

    return data, current_seg


async def fetch_segments_concurrent(name, seg_cnt):
    logging.info(f"Sending interests for root {name}")

    segments = []
    root_requests = []
    current_seg = 0
    while current_seg < min(int(seg_cnt),Config.config["max_packets"]):
        logging.info(f"Requesting segment {current_seg} of tree with root {name}")
        root_requests.append(send_interest(Name.normalize(name) + [Component.from_segment(current_seg)]))
        current_seg += 1
    segments.extend(await asyncio.gather(*root_requests))

    data = b''
    for _, _, segment in segments:
        data += bytes(segment)

    return data, current_seg


async def fetch_segments_sequential(name):
    logging.info(f"Sending interests for tree with root {name}")
    data = b''
    current_seg = 0
    while current_seg < Config.config["max_packets"]:
        logging.info(f"Requesting segment {current_seg} of tree with root {name}")
        data_name, meta_info, seg = await send_interest(Name.normalize(name) + [Component.from_segment(current_seg)])
        data += bytes(seg)
        if meta_info.final_block_id == Component.from_segment(current_seg):
            break
        current_seg += 1

    return data, current_seg


async def fetch_segments_batch(name, batch_size):
    segments = []
    current_seg = 0
    logging.info(f"Sending initial interest for tree with root {name}")
    data_name, meta_info, seg = await send_interest(Name.normalize(name) + [Component.from_segment(current_seg)])
    segments.append((data_name, meta_info, seg))

    if meta_info.final_block_id != Component.from_segment(0):
        current_seg = 1
        batch = 0
        seg_requests = []
        while current_seg < Config.config["max_packets"]:
            logging.info(f"Requesting batch {batch} of tree with root {name}")
            for i in range(current_seg, min(current_seg + batch_size,Config.config["max_packets"])):
                logging.info(f"Requesting segment {current_seg} of tree with root {name}")
                seg_requests.append(send_interest(Name.normalize(name) + [Component.from_segment(current_seg)]))
                if meta_info.final_block_id == Component.from_segment(current_seg):
                    break
                current_seg += 1
            segments.extend(await asyncio.gather(*seg_requests))
            if meta_info.final_block_id == Component.from_segment(current_seg):
                break
            batch += 1

    data = b''
    for _, _, segment in segments:
        data += bytes(segment)

    return data, current_seg


async def send_sync_request(route, root_hash, asset_name, seg_cnt):
    name = route + Config.config["multi_path"] + f"{asset_name}" + f"/i" + f"/{root_hash}" + f"/{Config.geocode}" + f"/{seg_cnt}"
    await send_interest(name, 5)
    return
