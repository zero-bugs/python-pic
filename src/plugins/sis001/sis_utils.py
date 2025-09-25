#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
# @File        : sis_utils.py
# @Author      : anonymous
# @Time        : 2025/5/31 16:07
# @Description :
"""
import os
import re

from loguru import logger

from common.http.http_utils import HttpUtils

LOGGER = logger.bind(module_name="sis_utils")


class SisUtils:
    @staticmethod
    def download_image(url, name):
        if os.path.exists(name):
            return
        status, response = HttpUtils.fetch_with_retry_binary(url)
        if response is None:
            LOGGER.warning("image:{}, response is null.", url)
            return None

        LOGGER.info(f"downloading image id:{url}, path:{name}")
        if response.status_code == 200:
            with open(name, "wb") as f:
                f.write(response.content)

    @staticmethod
    def write_summary(text: str, name):
        if os.path.exists(name):
            return
        if text is None:
            return

        summary_list = list()
        text_arr = text.split("\n")
        for line in text_arr:
            if line.strip() == "":
                continue
            if line.startswith("【某某门事件】"):
                continue
            summary_list.append(line.strip())

        with open(name, "w", encoding="utf-8") as f:
            f.write("\n".join(summary_list))

    @staticmethod
    def validate_title(title):
        rstr = r"[\/\\\:\*\?\"\<\>\|]"  # '/ \ : * ? " < > |'
        new_title = re.sub(rstr, "_", title)  # 替换为下划线
        return new_title
