import logging
import asyncio
from pympler import asizeof
from typing import Optional

from ndn.encoding import Name, InterestParam, BinaryStr, FormalName, MetaInfo
from ndn.encoding import Name, Component

import Config
from Interests import send_root_request, send_asset_request


def on_direct_root_hash_interest(name: FormalName, param: InterestParam, app_param: Optional[BinaryStr]) -> None:
    """
    Callback function to handle an interest for a root hash, will respond with the signed packets with recent updates queue associated with the tree at the time of having the given root hash

    Args:
        name: Name requested
        param: Interest parameters
        app_param: Optional interest parameters
    """

    logging.info(f"Received direct root hash interest {Name.to_str(name)}")

    packets, seg_cnt, asset_name = Config.packed_updates_dict[Name.to_str(name).split("/")[-2]]
    seg_no = Component.to_number(name[-1])

    if seg_no < seg_cnt:
        Config.app.put_raw_packet(packets[Component.to_number(name[-1])])

    logging.info(f"Returned response for direct root hash interest {Name.to_str(name)}")
    return


def on_direct_geocode_interest(name: FormalName, param: InterestParam, app_param: Optional[BinaryStr]) -> None:
    """
    Callback function to handle an interest for the tree associated with the given geocode, will respond with the signed packets with the tree associated with the given geocode

    Args:
        name: Name requested
        param: Interest parameters
        app_param: Optional interest parameters
    """

    logging.info(f"Received direct geocode interest for {Name.to_str(name)}")

    packets, seg_cnt = Config.packed_tree_geocode
    seg_no = Component.to_number(name[-1])

    if seg_no < seg_cnt:
        Config.app.put_raw_packet(packets[Component.to_number(name[-1])])

    logging.info(f"Returned response for direct geocode interest for {Name.to_str(name)}")
    return


def on_direct_asset_interest(name: FormalName, param: InterestParam, app_param: Optional[BinaryStr]) -> None:
    """
    Callback function to handle interest for an asset, will respond with signed packets responding to the desired asset

    Args:
        name: Name requested
        param: Interest parameters
        app_param: Optional interest parameters
    """

    asset_name = "/".join(Name.to_str(name).split("/")[4:-1])
    logging.info(f"Received direct asset interest for {asset_name}")

    packets, seg_cnt = Config.packed_assets_dict[f"/{asset_name}"]
    seg_no = Component.to_number(name[-1])

    if seg_no < seg_cnt:
        Config.app.put_raw_packet(packets[Component.to_number(name[-1])])

    logging.info(f"Returned response for direct asset interest for {asset_name}")
    return


def on_init_interest(name: FormalName, param: InterestParam, app_param: Optional[BinaryStr]) -> None:
    """
    Callback function to handle test interest for setting up FIB tables, will respond with meaningless data packet

    Args:
        name: Name requested
        param: Interest parameters
        app_param: Optional interest parameters
    """

    logging.info(f"Init interest received for {Name.to_str(name)}")
    Config.app.put_data(name, content="received".encode(), freshness_period=1000)
    logging.info(f"Returned response for init interest received for {Name.to_str(name)}")
    return


def on_multi_interest(name: FormalName, param: InterestParam, app_param: Optional[BinaryStr]) -> None:
    """
    Callback function to handle multicast interest, continues the sync protocol by checking if the tree needs to be updated and requesting the necessary data as needed.

    Args:
        name: Name requested
        param: Interest parameters
        app_param: Optional interest parameters
    """

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
        logging.info(f"Checking hash {root_hash}")
        if Config.spasy.is_newer_tree(geocode, root_hash):
            logging.info(f"Checking action {action}")
            if Config.spasy.can_request_item(action):
                logging.info('Requesting data')
                asyncio.create_task(update_tree(root_hash, seg_cnt))
                if Config.config["request_asset"]:
                    asyncio.create_task(request_asset(asset_name))
            else:
                logging.info('There was a deletion, so there is no named data to request.')
        else:
            logging.info(f"Old tree with hash {root_hash} received")
    else:
        logging.info(f"Tree with geocode {geocode} not subscribed to")

    return


async def update_tree(root_hash: str, seg_cnt: int) -> None:
    """
    Requests data to update tree, this includes recent update queue and/or asset if desired. The recent update queue will be applied to the tree.

    Args:
        root_hash: Root hash of tree at time of recent update queue state
        seg_cnt: Number of packets received making up the recent update queue state
    """

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


async def request_asset(asset_name: str) -> None:
    """
    Request an asset by name

    Args:
        asset_name: Name of desired asset
    """

    name = Config.config["direct_asset_prefix"] + f"/{asset_name}"

    received_asset, num_seg = await send_asset_request(name)
    Config.timer.stop_global_timer("sync_update_data")
    logging.info(f"Received asset {asset_name}")

    return
