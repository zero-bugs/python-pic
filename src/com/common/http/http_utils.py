#!/usr/bin/env python
# -*- encoding: utf-8 -*-
import json
import logging
import requests
from requests.adapters import HTTPAdapter, Retry
from requests.exceptions import Timeout, RetryError


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
    def convert_json_to_meta(images:{}):
        result = []
        if images is None:
            return result

        image_array=json.loads(images)
        for image in image_array:
            uploader = UploaderMeta()
            uploader.username = image['uploader']['username']
            uploader.group = image['uploader']['group']

            tags = []


            imageMeta = ImageMeta()
            imageMeta.id = image['id']
            imageMeta.views = image['view']
            imageMeta.favorites = image['favorites']
            imageMeta.source = image['source']
            imageMeta.purity = image['purity']
            imageMeta.category = image['category']
            imageMeta.dimension_x = image['']
            imageMeta.dimension_y = image['']
            imageMeta.ratio = image['']
            imageMeta.file_size = image['']
            imageMeta.file_type = image['']
            imageMeta.created_at = image['']
            imageMeta.path = image['']
            imageMeta.tags = image['']
            imageMeta.uploader = uploader


    @staticmethod
    def download_wh_images(images, isStopAuto):
        pass
