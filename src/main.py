#!/usr/bin/env python
# -*- encoding: utf-8 -*-
import asyncio
import os

from common.log.log_print import Log
from wh.core.pic_manager import WhPicManager

# 日志初始化
Log.logging_init()

os.environ['NO_PROXY'] = 'localhost'

async def main() -> None:
    manager = WhPicManager()
    await manager.connect()
    await manager.get_ims_sorting_by_date_api(is_stop_auto=True, is_download=True)
    await manager.release()


async def main2() -> None:
    manager = WhPicManager()
    await manager.connect()
    await manager.backup_full_scan_and_download()
    await manager.release()

if __name__ == "__main__":
    asyncio.run(main())
