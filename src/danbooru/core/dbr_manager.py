#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
# @File        : dbr_manager.py
# @Author      : anonymous
# @Time        : 2024/10/26 21:44
# @Description :
"""
import time

from loguru import logger

from common.config.config_manager import ConfigManager
from common.constant.rating import RatingType
from common.http.http_utils import HttpUtils

LOGGER = logger.bind(module_name='danbooru')

class DbrManager:
    def __init__(self):
        pass

    async def get_ims_sorting_by_date_api(self, is_stop_auto=True, is_download=True):
        """
        从当前时间向历史遍历，获取图片
        功能1：列举图片，同时下载；
        功能2： 列举图片，但不下载，只更新数据库；
        :param is_stop_auto:
        :param is_download:
        :return:
        """

        rating_list = [RatingType.EXPLICIT, RatingType.QUESTIONABLE, RatingType.SAFE]
        url = ConfigManager.get_query_images_api()

        download_result = False
        for rating_type in rating_list:
            current_page = 0
            while True:
                current_page += 1
                params = {
                    "tags": "rating:{}".format(rating_type),
                    "page": current_page,
                }

                result = HttpUtils.fetch_with_retry_json(url, params=params, headers={})
                if result is {} or result is []:
                    logger.warning("all images has refreshed for rating:{}, total page:{}".format(rating_type, current_page))
                    break

                images = self.get_images_from_resp(result)
                await self.db_handler.batch_insert_table(images, list(), list())
                if is_download:
                    download_result = await self.download_wh_images(images)

                # 所有图片都无需下载时，不继续遍历
                if download_result and is_stop_auto:
                    LOGGER.warning("no need continue download, current page: {}, url: {}".format(current_page, url))
                    break

                time.sleep(0.5)

    def get_images_from_resp(self, data):
        images = list()
        if isinstance(data, list):
            for item in data:
                images.append(ImageMeta.build_json_obj(item))
        else:
            images.append(ImageMeta.build_json_obj(data))
        return images

