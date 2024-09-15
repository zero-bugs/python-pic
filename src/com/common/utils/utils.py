#!/usr/bin/env python
# -*- encoding: utf-8 -*-
import json
import logging
import os

LOGGER = logging.getLogger(__name__)


class Utils:
    """
    读取json格式的配置文件
    """

    @staticmethod
    def read_json_file(path: str):
        if not os.path.exists(path):
            LOGGER.info("json file:{} not exist.".format(path))
        else:
            return json.loads(path)
