#!/usr/bin/env python
# -*- encoding: utf-8 -*-
import json
import logging
import os
from datetime import datetime

LOGGER = logging.getLogger(__name__)


class Utils:
    """
    读取json格式的配置文件
    """
    TIME_FORMAT = '%Y-%m-%d %H:%M:%S'

    @staticmethod
    def read_json_file(path: str):
        if not os.path.exists(path):
            LOGGER.info("json file:{} not exist.".format(path))
        else:
            with open(path, 'r') as f:
                return json.load(f)

    @staticmethod
    def get_current_time():
        """
        :return: 返回当前时间字符串
        """
        return datetime.now().strftime(Utils.TIME_FORMAT)

    @staticmethod
    def get_datetime_from_str(date_str: str):
        return datetime.strptime(date_str, Utils.TIME_FORMAT)


    @staticmethod
    def get_year_and_month_from_str(date_str: str):
        return datetime.strftime(datetime.strptime(date_str, Utils.TIME_FORMAT), '%Y-%m')