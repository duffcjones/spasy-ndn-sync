import logging
import pickle
import asyncio
from typing import Optional

from ndn.types import InterestNack, InterestTimeout, InterestCanceled, ValidationFailure
from ndn.encoding import Name, Component, MetaInfo, FormalName, BinaryStr

import Config
from SpasyTree import SpasyTree


async def send_interest(name: Name, ttl: int = 5000) -> tuple[FormalName, MetaInfo, Optional[BinaryStr]]:
    """
    Send a single interest for the given name. Throws an exception if packet is not received properly.

    Args:
        name: Name of data (str)
        ttl: Time to live for interest packet (ms)

    Returns:
        data_name: Name of data (formal name)
        meta_info: Meta information of data response
        data: Binary data contained in response (BinaryStr)
    """

    data_name, meta_info, data = None, None, None
    try:
        logging.info(f"Sending interest for {Name.to_str(name)}")
        data_name, meta_info, data = await Config.app.express_interest(
            Name.normalize(name), must_be_fresh=False, can_be_prefix=True,
            lifetime=ttl)
        logging.info(f'Received response for {Name.to_str(data_name)}')
    except InterestNack as e:
        logging.info(f'Interest {Name.to_str(name)} nacked with reason={e.reason}')
    except InterestTimeout as e:
        logging.info(f'Interest {Name.to_str(name)} timed out')
    except InterestCanceled as e:
        logging.info(f'Interest {Name.to_str(name)} canceled')
    except ValidationFailure as e:
        logging.info(f'Interest {Name.to_str(name)} data failed to validate with reason={e.result}')
    except Exception as e:
        logging.info(f'Interest {Name.to_str(name)} error: {e}')
    finally:
        return data_name, meta_info, data


async def send_init_interests() -> None:
    """
    Send test interests to nodes in multicast list, sends sequentially and waits for each response
    """

    for route in Config.config["multi_cast_routes"]:
        name = route + Config.config["initialization_path"]
        await send_interest(name)
    return


async def send_root_request(name: Name, seg_cnt: int) -> tuple[list, int, Optional[BinaryStr]]:
    """
    Send request(s) for a root hash, sends requests concurrently and requires the total number of segments to send for be known in advance

    Args:
        name: Name containing root hash (str)
        seg_cnt: Total number of segments for requested update queue

    Returns:
        received_update: Unserialized update queue
        num_seg: Number of segments received making up update queue
        data: Unserialized update queue
    """

    data, num_seg = await fetch_segments_concurrent(name, seg_cnt)
    received_update = pickle.loads(data)
    logging.info(f"Received response for interest {name}")
    return received_update, num_seg, data


async def send_asset_request(name: Name) -> tuple[Optional[BinaryStr], int]:
    """
    Send request(s) for an asset, sends requests in concurrent batches with each batch being processed sequentially

    Args:
        name: Name of asset

    Returns:
        data: Binary data of asset
        num_seg: Number of segments received making up asset
    """

    data, num_seg = await fetch_segments_batch(name, Config.config["batch_size"])
    return data, num_seg


async def fetch_segments(name: Name) -> tuple[Optional[BinaryStr], int]:
    """
    Fetches all segments making up content with given name, done concurrently, with an initial interest being sent to determine the number of segments

    Args:
        name: Name of content

    Returns:
        data: Binary data of response
        current_seg: Total number of segments received making up response
    """

    segments = []
    current_seg = 0

    logging.info(f"Sending initial interest for tree with root {name}")
    data_name, meta_info, seg = await send_interest(Name.normalize(name) + [Component.from_segment(current_seg)])
    segments.append((data_name, meta_info, seg))

    if meta_info.final_block_id != Component.from_segment(0):
        requests = []
        current_seg = 1
        while current_seg < Config.config["max_packets"]:
            logging.info(f"Requesting segment {current_seg} of tree with root {name}")
            requests.append(send_interest(Name.normalize(name) + [Component.from_segment(current_seg)]))
            if meta_info.final_block_id == Component.from_segment(current_seg):
                break
            current_seg += 1
        segments.extend(await asyncio.gather(*requests))

    data = b''
    for _, _, segment in segments:
        data += bytes(segment)

    return data, current_seg


async def fetch_segments_concurrent(name: Name, seg_cnt: int) -> tuple[Optional[BinaryStr], int]:
    """
    Fetches all segments making up content with given name, done concurrently with all interests being sent without waiting for the previous segment.
    Requires that the total number of segments be known beforehand

    Args:
        name: Name of content
        seg_cnt: Total number of segments

    Returns:
        data: Binary data of response
        current_seg: Total number of segments received making up response
    """

    logging.info(f"Sending interests for root {name}")

    segments = []
    requests = []
    current_seg = 0

    while current_seg < min(int(seg_cnt), Config.config["max_packets"]):
        logging.info(f"Requesting segment {current_seg} of tree with root {name}")
        requests.append(send_interest(Name.normalize(name) + [Component.from_segment(current_seg)]))
        current_seg += 1
    segments.extend(await asyncio.gather(*requests))

    data = b''
    for _, _, segment in segments:
        data += bytes(segment)

    return data, current_seg


async def fetch_segments_sequential(name: Name) -> tuple[Optional[BinaryStr], int]:
    """
    Fetches all segments making up content with given name, done sequentially with each interest being sent after the previous segment has been received

    Args:
        name: Name of content

    Returns:
        data: Binary data of response
        current_seg: Total number of segments received making up response
    """

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


async def fetch_segments_batch(name: Name, batch_size: int) -> tuple[Optional[BinaryStr], int]:
    """
    Fetches all segments making up content with given name, done in batches. Each batch is processed concurrently,
    a batch of interests is sent only once all interests in the previous batch has received responses.

    Args:
        name: Name of content
        batch_size: Number of segments per batch

    Returns:
        data: Binary data of response
        current_seg: Total number of segments received making up response
    """

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
            for i in range(current_seg, min(current_seg + batch_size, Config.config["max_packets"])):
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


async def send_sync_request(route: str, root_hash: str, asset_name: str, seg_cnt: int) -> None:
    """
    Send notification request to a given node

    Args:
        route: Node prefix of desired node
        root_hash: Notification interest root hash
        asset_name: Name of asset associated with update
        seg_cnt: Number of segments making up update queue
    """

    name = route + Config.config["multi_path"] + f"{asset_name}" + f"/i" + f"/{root_hash}" + f"/{Config.geocode}" + f"/{seg_cnt}"
    await send_interest(name, 5)
    return
