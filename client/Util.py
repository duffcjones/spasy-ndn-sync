import logging
import pickle

from ndn.encoding import Name, Component

import Config


def pack_tree(tree, name):
    serialized_tree = pickle.dumps(tree)
    seg_cnt = (len(serialized_tree) + Config.config["packet_segment_size"] - 1) // Config.config["packet_segment_size"]
    logging.info(f"Packing tree under name {name}")

    packets = [Config.app.prepare_data(Name.normalize(name) + [Component.from_segment(i)],
                                serialized_tree[i * Config.config["packet_segment_size"]:(i + 1) * Config.config["packet_segment_size"]],
                                freshness_period=10000,
                                final_block_id=Component.from_segment(seg_cnt - 1),
                                no_signature=True)
               for i in range(seg_cnt)]

    logging.info(f"Packed tree with name {name} into {seg_cnt} segments")
    return packets, seg_cnt
