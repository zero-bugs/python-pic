#!/usr/bin/env python
# -*- encoding: utf-8 -*-
import json
import os
from datetime import datetime

from loguru import logger

LOGGER = logger.bind(module_name=__name__)


class ConfigUtils(object):
    """
    读取json格式的配置文件
    """

    TIME_FORMAT = "%Y-%m-%d %H:%M:%S"
    TIME_FORMAT_FILE = "%Y_%m_%d_%H_%M_%S"

    @staticmethod
    def read_json_file(path: str):
        if not os.path.exists(path):
            LOGGER.info(f"json file:{path} not exist.")
        else:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)

    @staticmethod
    def get_current_time():
        """
        :return: 返回当前时间字符串
        """
        return datetime.now().strftime(ConfigUtils.TIME_FORMAT)

    @staticmethod
    def get_current_time_for_file():
        """
        :return: 返回当前时间字符串
        """
        return datetime.now().strftime(ConfigUtils.TIME_FORMAT_FILE)

    @staticmethod
    def get_datetime_from_str(date_str: str):
        return datetime.strptime(date_str, ConfigUtils.TIME_FORMAT)

    @staticmethod
    def get_year_and_month_from_str(date_str: str):
        return datetime.strftime(
            datetime.strptime(date_str, ConfigUtils.TIME_FORMAT), "%Y-%m"
        )
