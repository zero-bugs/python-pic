#!/usr/bin/env python
# -*- encoding: utf-8 -*-
import json
import logging
import requests
from requests.adapters import HTTPAdapter, Retry
from requests.exceptions import Timeout, RetryError

from com.config.config_manager import ConfigManager
from com.wh.meta.image_meta import ImageMeta
from com.wh.meta.uploader_meta import UploaderMeta

LOGGER = logging.getLogger(__name__)


class HttpUtils:
    @staticmethod
    def fetch_with_retry(url: str, params: {}, headers: {}):
        """
        获取响应，有重试
        :param url:
        :param params
        :param headers
        :return:
        """
        result = {}

        response = None
        with requests.Session() as session:
            retries = Retry(
                total=3,
                backoff_factor=0.5,
                backoff_jitter=0.5,
                backoff_max=30,
                status_forcelist=[429, 500, 503])
            session.mount(url, HTTPAdapter(max_retries=retries))

            try:
                response = session.get(
                    url,
                    verify=True,
                    timeout=(3, 10),
                    params=params,
                    headers=headers,
                    proxies=ConfigManager.get_proxy_config(),
                )
            except Timeout as tx:
                LOGGER.warning("http timeout.", tx)
            except RetryError as rx:
                LOGGER.warning("retry error.", rx)
            except BaseException as bx:
                LOGGER.warning("unexpect error.", bx)

        if response is None:
            LOGGER.warning("url:{} not arrived.".format(url))

        if response.status_code != 200:
            LOGGER.warning("url:{} not arrived.".format(url))
            LOGGER.warning("request meet some issue: {}, msg:{}".format(response.status_code, response.text))
            return result

        return response.json()

    @staticmethod
    def convert_json_to_meta(images: {}):
        result = []
        if images is None:
            return result

        image_array = json.loads(images)
        for image in image_array:
            uploader = UploaderMeta()
            uploader.username = image['uploader']['username']
            uploader.group = image['uploader']['group']

            tags = []

            image_meta = ImageMeta()
            image_meta.id = image['id']
            image_meta.views = image['view']
            image_meta.favorites = image['favorites']
            image_meta.source = image['source']
            image_meta.purity = image['purity']
            image_meta.category = image['category']
            image_meta.dimension_x = image['']
            image_meta.dimension_y = image['']
            image_meta.ratio = image['']
            image_meta.file_size = image['']
            image_meta.file_type = image['']
            image_meta.created_at = image['']
            image_meta.path = image['']
            image_meta.tags = image['']
            image_meta.uploader = uploader

    @staticmethod
    def download_wh_images(images, is_stop_auto):
        pass
