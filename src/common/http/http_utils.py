#!/usr/bin/env python
# -*- encoding: utf-8 -*-
import logging

import requests
from requests.adapters import HTTPAdapter, Retry
from requests.exceptions import Timeout, RetryError

from common.config.config_manager import ConfigManager

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
                total=10,
                backoff_factor=0.5,
                backoff_max=300,
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
