#!/usr/bin/env python
# -*- encoding: utf-8 -*-
from com.common.http.http_utils import HttpUtils
from com.config.config_manager import ConfigManager


class WhPicManager:
    def get_imgs_sorting_by_data(self, isStopAuto=True):
        """
        从当前时间向历史遍历，获取图片
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

        HttpUtils.download_wh_images(images, isStopAuto)

        while current_page < last_page:
            current_page += current_page
            params['page'] = current_page

            result = HttpUtils.fetch_with_retry(url, params=params, headers=headers)
            images = result['data']
            HttpUtils.download_wh_images(images, isStopAuto)