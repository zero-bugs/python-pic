#!/usr/bin/env python
# -*- encoding: utf-8 -*-
import os
import time

from prisma.models import WhImage, Uploader, Tag

from com.common.http.http_utils import HttpUtils
from com.config.config_manager import ConfigManager
from com.wh.db.wh_db_handler import WhDbHandler
from com.wh.meta.image_meta import ImageMeta


class WhPicManager:
    def __init__(self):
        self.db_handler = WhDbHandler()
        self.api_key = ConfigManager.get_api_key()

    async def connect(self):
        await self.db_handler.connect()

    async def release(self):
        await self.db_handler.release()

    async def get_ims_sorting_by_data(self, is_stop_auto=True, is_download=True):
        """
        从当前时间向历史遍历，获取图片
        功能1：列举图片，同时下载；
        功能2： 列举图片，但不下载，只更新数据库；
        :param is_stop_auto:
        :param is_download:
        :return:
        """

        url = ConfigManager.get_wh_query_images_api()
        params = {
            "categories": "111",
            "purity": "001",
            "sorting": "date_added*",
            "order": "desc*",
            "apikey": self.api_key
        }
        headers = {}

        result = HttpUtils.fetch_with_retry(url, params=params, headers=headers)
        meta = result['meta']
        data = result['data']

        current_page = 0
        per_page = 0
        last_page = 0
        if meta is not None:
            last_page = meta['last_page']
            per_page = meta['per_page']

        images = self.get_images_from_resp(data)
        await self.db_handler.batch_insert_images(images, list(), list())
        if is_download:
            HttpUtils.download_wh_images(images, is_stop_auto)
            await self.db_handler.batch_update_images_status(images, 3)

        while current_page < last_page:
            current_page += 1
            params['page'] = current_page

            result = HttpUtils.fetch_with_retry(url, params=params, headers=headers)
            data = result['data']

            images = self.get_images_from_resp(data)
            await self.db_handler.batch_insert_images(images, list(), list())
            if is_download:
                HttpUtils.download_wh_images(images, is_stop_auto)
                await self.db_handler.batch_update_images_status(images, 3)

            time.sleep(0.5)

    def get_images_from_resp(self, data: dict[str]):
        images = list()
        if isinstance(data, list):
            for item in data:
                images.append(ImageMeta.build_json_obj(item))
        else:
            images.append(ImageMeta.build_json_obj(data))
        return images
