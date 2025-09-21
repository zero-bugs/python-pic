#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
# @File        : main_cosblay.py
# @Author      : anonymous
# @Time        : 2025/9/15 23:10
# @Description :
"""
import asyncio
import os

from loguru import logger

from common.log.log_print import LogUtils
from plugins.cosblay.cosblay_page_manager import CosBlayPageManager

# 日志初始化
LogUtils.logging_init_loguru()
os.environ["NO_PROXY"] = "localhost"

TASK_LIST = (
    "https://cn.cosblay.com/2024/%e4%b8%83%e6%b5%b7gz-press-%e5%af%ab%e7%9c%9f%e9%9b%86-no-490-612-%e5%9c%96%e7%89%87.html/2",
)

LOGGER = logger.bind(module_name="cosblay")


async def main() -> None:
    cos_manager = CosBlayPageManager()
    for task in TASK_LIST:
        await cos_manager.template_get_link_from_detail_page(task)

    # await cos_manager.template_get_links_by_list("https://www.hongimg.com", "色情")


if __name__ == "__main__":
    asyncio.run(main())
