from ndn.app import NDNApp
from ndn.encoding import Name, InterestParam, BinaryStr, FormalName, MetaInfo
from ndn.types import InterestNack, InterestTimeout, InterestCanceled, ValidationFailure

import logging
import argparse

logging.basicConfig(
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.DEBUG)


async def main(prefix):
    try:
        name = Name.from_str(prefix)
        logging.info(f'Sending Interest {Name.to_str(name)}, {InterestParam(must_be_fresh=True, lifetime=6000)}')
        data_name, meta_info, content = await app.express_interest(
            prefix, must_be_fresh=True, can_be_prefix=False, lifetime=6000)

        logging.info(f'Received Data Name: {Name.to_str(data_name)}')
        logging.info(meta_info)
        logging.info(bytes(content) if content else None)

    except InterestNack as e:
        logging.info(f'Nacked with reason={e.reason}')
    except InterestTimeout:
        logging.info(f'Timeout')
    except InterestCanceled:
        logging.info(f'Canceled')
    except ValidationFailure:
        logging.info(f'Data failed to validate')
    finally:
        app.shutdown()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("prefix")
    args = parser.parse_args()
    app = NDNApp()
    app.run_forever(after_start=main(args.prefix))
