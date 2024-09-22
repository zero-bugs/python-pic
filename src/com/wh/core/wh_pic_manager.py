#!/usr/bin/env python
# -*- encoding: utf-8 -*-
from com.common.http.http_utils import HttpUtils
from com.config.config_manager import ConfigManager
from com.wh.db.wh_db_handler import WhDbHandler


class WhPicManager:
    def __init__(self):
        self.db_handler = WhDbHandler()

    def get_imgs_sorting_by_data(self, is_stop_auto=True, is_download=True):
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
            "categories": 111,
            "purity": 111,
            "sorting": "date_added*",
            "order": "desc*",
        }
        headers = {}

        result = HttpUtils.fetch_with_retry(url, params=params, headers=headers)
        meta = result['meta']
        images = result['data']

        current_page = 0
        per_page = 0
        last_page = 0
        if meta is not None:
            last_page = meta['last_page']
            per_page = meta['per_page']

        self.db_handler.batch_insert_images(images)
        if is_download:
            HttpUtils.download_wh_images(images, is_stop_auto)
            self.db_handler.batch_update_images(images, 3)

        while current_page < last_page:
            current_page += current_page
            params['page'] = current_page

            result = HttpUtils.fetch_with_retry(url, params=params, headers=headers)
            images = result['data']
            self.db_handler.batch_insert_images(images)
            if is_download:
                HttpUtils.download_wh_images(images, is_stop_auto)
                self.db_handler.batch_update_images(images, 3)