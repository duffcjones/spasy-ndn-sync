from ndn.app import NDNApp
from ndn.encoding import Name, InterestParam, BinaryStr, FormalName, MetaInfo

from typing import Optional

import logging

logging.basicConfig(
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.DEBUG)

prefix = "/example/1"
app = NDNApp()


async def main():
    logging.info("app stuff")
    pass


@app.route(prefix)
def on_interest(name: FormalName, param: InterestParam, app_param: Optional[BinaryStr]):
    pass


if __name__ == '__main__':
    logging.info("app run")
    app.run_forever(after_start=main())
