#!/usr/bin/env python
# -*- encoding: utf-8 -*-
import asyncio
import os

from common.log.log_print import LogUtils
from fp.core.page_manager import FpPageManager
from wh.core.pic_manager import WhPicManager

# 日志初始化
LogUtils.logging_init()

os.environ['NO_PROXY'] = 'localhost'


async def main() -> None:
    manager = WhPicManager()
    await manager.connect()
    await manager.get_ims_sorting_by_date_api(is_stop_auto=True, is_download=True)
    await manager.release()


async def main2() -> None:
    manager = WhPicManager()
    await manager.connect()
    await manager.background_full_scan_and_download()
    await manager.release()


async def main3() -> None:
    manager = FpPageManager()
    await manager.connect()
    await manager.get_all_actresses_list()
    await manager.get_all_actresses_list_by_inventory()
    await manager.get_all_resources_list_by_article()
    await manager.release()


async def main4() -> None:
    manager = FpPageManager()
    await manager.connect()
    await manager.download_all_resources_by_link()
    await manager.release()


if __name__ == "__main__":
    # asyncio.run(main())
    # asyncio.run(main3())
    asyncio.run(main4())
