from ndn.types import InterestNack, InterestTimeout, InterestCanceled, ValidationFailure
from ndn.encoding import Name, Component

import logging
import pickle

import Config


async def send_init_interest(route):
    name = route + Config.config["initialization_postfix"]
    data_name, meta_info, seg = await Config.app.express_interest(
        Name.normalize(name), must_be_fresh=True, can_be_prefix=True,
        lifetime=100)


async def send_root_request(name):
    received_tree = None
    try:
        data = b''
        seg_no = 0
        num_seg, data = await fetch_segments(name)
        received_tree = pickle.loads(data)
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
        return received_tree

async def fetch_segments(name):
    data = b''
    seg_no = 0
    while seg_no < 100:
        data_name, meta_info, seg = await Config.app.express_interest(
            Name.normalize(name) + [Component.from_segment(seg_no)], must_be_fresh=True, can_be_prefix=True,
            lifetime=100)

        data += bytes(seg)
        if meta_info.final_block_id == Component.from_segment(seg_no):
            break
        else:
            seg_no += 1

    return seg_no, data


async def send_sync_request(route, root_hash):
    name = route + Config.config["multi_postfix"] + Config.config["direct_prefix"] + root_hash

    try:
        data_name, meta_info, response = await Config.app.express_interest(
            Name.normalize(name), must_be_fresh=True, can_be_prefix=True, lifetime=100)
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
