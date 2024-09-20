from ndn.encoding import Name, InterestParam, BinaryStr, FormalName, MetaInfo
from ndn.encoding import Name, Component

from typing import Optional
import logging
import asyncio

import Config
from Interests import send_root_request

def on_direct_interest(name, param, app_param):
    packets, seg_cnt = Config.packed_trees[Name.to_str(name).rsplit("/",1)[0]]
    seg_no = Component.to_number(name[-1])

    if seg_no < seg_cnt:
        Config.app.put_raw_packet(packets[Component.to_number(name[-1])])

def on_init_interest(name, param, app_param):
    logging.info(f"Init interest received for {name}")
    Config.app.put_data(name, content="received".encode(), freshness_period=100)

def on_multi_interest(name: FormalName, param: InterestParam, app_param: Optional[BinaryStr]):
    logging.info(f"Multi Interest received for {name}")
    global content
    Config.app.put_data(name, content="received".encode(), freshness_period=100)
    name = Name.to_str(name)
    sender = "/" + name.split("//")[-1].rsplit("/", 1)[0]
    root_hash = name.split("/")[-1]
    asyncio.create_task(receive_hash(root_hash,sender))

async def receive_hash(root_hash, sender):
    name = sender + "/" + root_hash
    received_tree = await send_root_request(name)
