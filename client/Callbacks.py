from ndn.encoding import Name, InterestParam, BinaryStr, FormalName, MetaInfo
from ndn.encoding import Name, Component

from typing import Optional
import logging
import asyncio
from pympler import asizeof

import Config
from Interests import send_root_request

def on_direct_root_hash_interest(name: FormalName, param: InterestParam, app_param: Optional[BinaryStr]):
    logging.info(f"Received direct root hash interest {Name.to_str(name)}")

    packets, seg_cnt = Config.packed_updates_dict[Name.to_str(name).split("/")[-2]]
    seg_no = Component.to_number(name[-1])

    if seg_no < seg_cnt:
        Config.app.put_raw_packet(packets[Component.to_number(name[-1])])

    logging.info(f"Returned response for direct root hash interest {Name.to_str(name)}")
    return


def on_direct_geocode_interest(name: FormalName, param: InterestParam, app_param: Optional[BinaryStr]):
    logging.info(f"Received direct geocode interest for {Name.to_str(name)}")

    packets, seg_cnt = Config.packed_tree_geocode
    seg_no = Component.to_number(name[-1])

    if seg_no < seg_cnt:
        Config.app.put_raw_packet(packets[Component.to_number(name[-1])])

    logging.info(f"Returned response for direct geocode interest for {Name.to_str(name)}")
    return


def on_init_interest(name: FormalName, param: InterestParam, app_param: Optional[BinaryStr]):
    logging.info(f"Init interest received for {Name.to_str(name)}")
    Config.app.put_data(name, content="received".encode(), freshness_period=1000)
    logging.info(f"Returned response for init interest received for {Name.to_str(name)}")
    return


def on_multi_interest(name: FormalName, param: InterestParam, app_param: Optional[BinaryStr]):
    Config.timer.stop_global_timer("notification_interest")
    logging.info(f"Multi Interest received for {Name.to_str(name)}")

    name = Name.to_str(name)
    partitions = name.split("/")
    root_hash = partitions[-3]
    seg_cnt = partitions[-1]

    if Config.spasy.is_newer_tree(Config.geocode, root_hash):
        asyncio.create_task(receive_hash(root_hash, seg_cnt))
    else:
        logging.info(f"Old tree with hash {root_hash} received")
    return


async def receive_hash(root_hash, seg_cnt):
    name = Config.config["direct_root_hash_prefix"] + f"/{root_hash}"

    Config.timer.start_timer(f"receive_updates")
    received_updates, data = await send_root_request(name, seg_cnt)
    # await send_root_request(name, seg_cnt)
    Config.timer.stop_timer(f"receive_updates")

    # Config.timer.start_timer(f"update_tree")
    # Config.spasy.update_tree(Config.geocode, received_updates)
    # Config.timer.stop_timer(f"update_tree")
    #
    # Config.timer.stop_global_timer("sync_update")
    # logging.info("Stopping sync_update timer")
    #
    # logging.info(f"Received new tree updates with resulting hash {root_hash} of size {asizeof.asizeof(received_updates)}")
    # Config.stats.record_stat(f"{Config.config["node_name"]}_received_tree_update_uncompressed", asizeof.asizeof(received_updates))
    # Config.stats.record_stat(f"{Config.config["node_name"]}_received_tree_update_compressed", asizeof.asizeof(data))
    return
