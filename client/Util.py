import logging
from ndn.encoding import Name, Component

import Config

# def pack_tree(serialized_tree, root_hash):
#     seg_cnt = (len(serialized_tree) + Config.config["packet_segment_size"] - 1) // Config.config["packet_segment_size"]
#     name = Config.config["direct_prefix"] + root_hash
#
#     packets = [Config.app.prepare_data(Name.normalize(name) + [Component.from_segment(i)],
#                                 serialized_tree[i * Config.config["packet_segment_size"]:(i + 1) * Config.config["packet_segment_size"]],
#                                 freshness_period=10000,
#                                 final_block_id=Component.from_segment(seg_cnt - 1),
#                                 no_signature=True)
#                for i in range(seg_cnt)]
#
#     Config.packed_trees[Name.to_str(name)] = (packets, seg_cnt)
#     logging.info(f"Packed {seg_cnt} segments")

def pack_tree(serialized_tree, root_hash):
    seg_cnt = (len(serialized_tree) + Config.config["packet_segment_size"] - 1) // Config.config["packet_segment_size"]
    name = Config.config["direct_prefix"] + f"/{root_hash}"
    logging.info(f"Packing under name {name}")

    packets = [Config.app.prepare_data(Name.normalize(name) + [Component.from_segment(i)],
                                serialized_tree[i * Config.config["packet_segment_size"]:(i + 1) * Config.config["packet_segment_size"]],
                                freshness_period=10000,
                                final_block_id=Component.from_segment(seg_cnt - 1),
                                no_signature=True)
               for i in range(seg_cnt)]

    # Config.packed_trees[Name.to_str(name)] = (packets, seg_cnt)
    Config.packed_trees[root_hash] = (packets, seg_cnt)
    logging.info(f"Packed {seg_cnt} segments")
    return seg_cnt - 1
