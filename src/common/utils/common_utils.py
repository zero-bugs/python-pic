#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
# @File        : common_utils.py
# @Author      : anonymous
# @Time        : 2025/9/21 10:20
# @Description :
"""
import time

from loguru import logger

LOGGER = logger.bind(module_name=__name__)


class CommonUtils(object):
    @staticmethod
    def waiting_with_print(count: int):
        interval = int(count / 10)
        remainder = count % 10
        for i in range(interval):
            LOGGER.info("waiting 10s....")
            time.sleep(10)

        if remainder > 0:
            LOGGER.info(f"waiting {remainder}s....")
            time.sleep(remainder)
