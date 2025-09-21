#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
# @File        : file_utils.py
# @Author      : anonymous
# @Time        : 2025/9/21 10:16
# @Description :
"""
import os
import re
from random import random

from loguru import logger

from common.utils.config_utils import ConfigUtils

LOGGER = logger.bind(module_name=__name__)


class FileUtils:
    """
    文件输入输出工具
    """

    @staticmethod
    def normalize_windows_path(path):
        template = r"[\/\\\:\*\?\"\<\>\|]"
        return re.sub(template, "_", path)

    @staticmethod
    def normalize_str(title):
        rstr = r"[\/\\\:\*\?\"\<\>\|]"  # '/ \ : * ? " < > |'
        new_title = re.sub(rstr, "_", title)  # 替换为下划线
        return new_title

    @staticmethod
    def basic_file_write(file_name, content: str, overwrite=False):
        """
        基础下载工具
        :param file_name: 全路径，外部需要保证输入文件名合法
        :param content: 内容
        :param overwrite:
        :return:
        """

        if os.path.exists(os.path.dirname(file_name)):
            os.makedirs(os.path.dirname(file_name), exist_ok=True)

        if not overwrite and os.path.exists(file_name):
            return

        with open(file_name, "w") as f:
            f.write(content + "\n")

    @staticmethod
    def write_list_to_file(file_name, content: list, overwrite=False):
        """
        将列表内容打印出来，如果list内部是obj，需要实现__str__函数
        :param file_name:全路径，外部需要保证输入文件名合法
        :param content:内容
        :param overwrite:
        :return:
        """
        if os.path.exists(os.path.dirname(file_name)):
            os.makedirs(os.path.dirname(file_name), exist_ok=True)

        if not overwrite and os.path.exists(file_name):
            cur_time = ConfigUtils.get_current_time()
            index = file_name.rfind(".")
            file_name = file_name[:index] + "_" + cur_time + "." + file_name[index + 1:]

        if not content or len(content) == 0:
            return
        with open(file_name, "w") as f:
            for ctt in content:
                f.write(ctt.__str__() + "\n")
