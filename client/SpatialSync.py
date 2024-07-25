from ndn.app import NDNApp
from ndn.encoding import Name, InterestParam, BinaryStr, FormalName, MetaInfo
from ndn.types import InterestNack, InterestTimeout, InterestCanceled, ValidationFailure

from typing import Optional
import logging
import argparse

logging.basicConfig(
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.DEBUG)

content = ""


async def main(source, target):
    content = source
    await app.register(source, on_interest)
    logging.info("app stuff")
    receivedInterest = False

    while not receivedInterest:
        try:
            name = Name.from_str(target)
            logging.info(f'Sending Interest {Name.to_str(name)}, {InterestParam(must_be_fresh=True, lifetime=6000)}')
            data_name, meta_info, content = await app.express_interest(
                target, must_be_fresh=True, can_be_prefix=False, lifetime=6000)

            logging.info(f'Received Data Name: {Name.to_str(data_name)}')
            logging.info(meta_info)
            logging.info(bytes(content) if content else None)
            receivedInterest = True
        except InterestNack as e:
            logging.info(f'Nacked with reason={e.reason}')
        except InterestTimeout:
            logging.info(f'Timeout')
        except InterestCanceled:
            logging.info(f'Canceled')
        except ValidationFailure:
            logging.info(f'Data failed to validate')

    app.shutdown()


def on_interest(name: FormalName, param: InterestParam, app_param: Optional[BinaryStr]):
    logging.info(f'>> Interest: {Name.to_str(name)}, {param}')
    app.put_data(name, content=content.encode(), freshness_period=10000)
    logging.info(f'<< Data: {Name.to_str(name)}')
    logging.info(MetaInfo(freshness_period=10000))
    logging.info(f'Content: (size: {len(content)})')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("source")
    parser.add_argument('--target', dest='target')
    args = parser.parse_args()
    logging.info("app run")
    app = NDNApp()

    app.run_forever(after_start=main(args.source, args.target))
