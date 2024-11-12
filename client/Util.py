import logging

from ndn.encoding import Name, Component

import Config


def pack_data(data, name):
    seg_cnt = (len(data) + Config.config["packet_segment_size"] - 1) // Config.config["packet_segment_size"]
    logging.info(f"Packing data under name {name}")

    packets = [Config.app.prepare_data(Name.normalize(name) + [Component.from_segment(i)],
                                data[i * Config.config["packet_segment_size"]:(i + 1) * Config.config["packet_segment_size"]],
                                freshness_period=100000,
                                final_block_id=Component.from_segment(seg_cnt - 1),)
               for i in range(seg_cnt)]

    logging.info(f"Packed data with name {name} into {seg_cnt} segments")
    return packets, seg_cnt
