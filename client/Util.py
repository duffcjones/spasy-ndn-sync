import logging

from ndn.encoding import Name, Component
from ndn.encoding.tlv_type import VarBinaryStr

import Config


def pack_data(data: any, name: str) -> tuple[list[VarBinaryStr], int]:
    """
    Split given data (binary) into signed packets based on configured packet size

    Args:
        data: Binary data to pack
        name: Name of content

    Returns:
        packets: List of packets making up given content
        seg_cnt: Number of segments making up given content
    """

    logging.info(f"Packing data under name {name}")

    seg_cnt = (len(data) + Config.config["packet_segment_size"] - 1) // Config.config["packet_segment_size"]
    packets = [Config.app.prepare_data(Name.normalize(name) + [Component.from_segment(i)],
                                data[i * Config.config["packet_segment_size"]:(i + 1) * Config.config["packet_segment_size"]],
                                freshness_period=100000,
                                final_block_id=Component.from_segment(seg_cnt - 1))
               for i in range(seg_cnt)]

    logging.info(f"Packed data with name {name} into {seg_cnt} segments")
    return packets, seg_cnt
