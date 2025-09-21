#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
# @File        : main_sis001.py
# @Author      : anonymous
# @Time        : 2025/5/21 21:39
# @Description :
"""
import asyncio
import os

from loguru import logger

from common.log.log_print import LogUtils
from plugins.sis001.sis_page_manager import SisPageManager

# 日志初始化
LogUtils.logging_init_loguru()
os.environ["NO_PROXY"] = "localhost"

LOGGER = logger.bind(module_name="sis001")


async def main() -> None:
    sis_manager = SisPageManager()
    await sis_manager.template_get_all_link_by_start_recursion(
        "thread-12190193-1-1.html"
    )


if __name__ == "__main__":
    asyncio.run(main())
