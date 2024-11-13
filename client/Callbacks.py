from ndn.encoding import Name, InterestParam, BinaryStr, FormalName, MetaInfo
from ndn.encoding import Name, Component

from typing import Optional
import logging
import asyncio
from pympler import asizeof

import Config
from Interests import send_root_request, send_asset_request

def on_direct_root_hash_interest(name: FormalName, param: InterestParam, app_param: Optional[BinaryStr]):
    logging.info(f"Received direct root hash interest {Name.to_str(name)}")

    packets, seg_cnt, asset_name = Config.packed_updates_dict[Name.to_str(name).split("/")[-2]]
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

def on_direct_asset_interest(name: FormalName, param: InterestParam, app_param: Optional[BinaryStr]):
    logging.info(f"Received direct asset interest for {"/".join(Name.to_str(name).split("/")[4:-1])}")

    packets, seg_cnt = Config.packed_assets_dict["/" + "/".join(Name.to_str(name).split("/")[4:-1])]
    seg_no = Component.to_number(name[-1])

    if seg_no < seg_cnt:
        Config.app.put_raw_packet(packets[Component.to_number(name[-1])])

    logging.info(f"Returned response for direct asset interest for {Name.to_str(name).split("/")[3:-2]}")


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
    asset_name = "/".join(partitions[4:-4])
    action = partitions[-4]
    root_hash = partitions[-3]
    geocode = partitions[-2]
    seg_cnt = partitions[-1]

    logging.info(f"Checking asset name {asset_name}")
    if Config.spasy.is_subscribed(asset_name):
        logging.info('This tree is subscribed to.')
        logging.info(f"Checking hash {root_hash}")
        if Config.spasy.is_newer_tree(geocode, root_hash):
            logging.info(f"Checking action {action}")
            if Config.spasy.can_request_item(action):
                logging.info('The item was inserted, so the named data may be requested.')
                asyncio.create_task(receive_hash(root_hash, seg_cnt))
                if Config.config["request_asset"]:
                    asyncio.create_task(receive_asset(asset_name))
            else:
                logging.info('There was a deletion, so there is no named data to request.')
        else:
            logging.info(f"Old tree with hash {root_hash} received")
    else:
        logging.info(f"Tree with geocode {geocode} not subscribed to")

    return


async def receive_hash(root_hash, seg_cnt):
    name = Config.config["direct_root_hash_prefix"] + f"/{root_hash}"

    Config.timer.start_timer(f"receive_updates")
    received_update, num_seg, data = await send_root_request(name, seg_cnt)
    Config.timer.stop_timer(f"receive_updates")

    Config.timer.start_timer(f"update_tree")
    Config.spasy.update_tree(Config.geocode, received_update)
    Config.timer.stop_timer(f"update_tree")

    Config.timer.stop_global_timer("sync_update")
    logging.info("Stopping sync_update timer")

    logging.info(f"Received new tree updates with resulting hash {root_hash} of size {asizeof.asizeof(received_update)}")
    Config.stats.record_stat(f"{Config.config["node_name"]}_received_tree_update_uncompressed", asizeof.asizeof(received_update))
    Config.stats.record_stat(f"{Config.config["node_name"]}_received_tree_update_compressed", asizeof.asizeof(data))
    return


async def receive_asset(asset_name):
    name = Config.config["direct_asset_prefix"] + f"/{asset_name}"

    received_asset, num_seg = await send_asset_request(name)
    Config.timer.stop_global_timer("sync_update_data")
    logging.info(f"Received asset {asset_name}")

    return
