import logging
import pickle

from ndn.encoding import Name, Component

import Config

from pympler import asizeof


def pack_data(data, name):
    serialized_data = pickle.dumps(data)
    logging.info(f"size {asizeof.asizeof(serialized_data)}")
    seg_cnt = (len(serialized_data) + Config.config["packet_segment_size"] - 1) // Config.config["packet_segment_size"]
    logging.info(f"Packing data under name {name}")

    packets = [Config.app.prepare_data(Name.normalize(name) + [Component.from_segment(i)],
                                serialized_data[i * Config.config["packet_segment_size"]:(i + 1) * Config.config["packet_segment_size"]],
                                freshness_period=100000,
                                final_block_id=Component.from_segment(seg_cnt - 1),)
               for i in range(seg_cnt)]
    logging.info(Config.timer.timers)

    logging.info(f"packet size is {asizeof.asizeof(packets[0])}")

    logging.info(f"Packed data with name {name} into {seg_cnt} segments")
    return packets, seg_cnt, serialized_data
