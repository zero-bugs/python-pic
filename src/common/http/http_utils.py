#!/usr/bin/env python
# -*- encoding: utf-8 -*-
import logging

import requests
from requests import HTTPError
from requests.adapters import HTTPAdapter, Retry
from requests.exceptions import RetryError, ProxyError, SSLError

from common.config.config_manager import ConfigManager
from common.config.link_status import LinkStatus

LOGGER = logging.getLogger('common')


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
        response = None
        status = LinkStatus.INITIAL
        with requests.Session() as session:
            retries = Retry(
                total=5,
                backoff_factor=1,
                backoff_max=60,
                status_forcelist=[429, 500, 502, 503, 504])
            session.mount(url, HTTPAdapter(max_retries=retries))

            if headers is None or headers is {}:
                headers = {
                    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                    'accept-encoding': 'gzip, deflate, br',
                    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36',
                },

            try:
                response = session.get(
                    url,
                    verify=True,
                    timeout=(3, 10),
                    params=params,
                    headers=headers,
                    allow_redirects=False,
                    proxies=ConfigManager.get_proxy_config(),
                )
            except HTTPError as he:
                LOGGER.error("http error.", he)
            # except ConnectTimeout as ce:
            #     LOGGER.warning("url:{} not arrived. error:".format(url), ce)
            #     status = LinkStatus.DOING
            # except ReadTimeout as re:
            #     LOGGER.warning("read timeout.", re)
            #     status = LinkStatus.DOING
            # except Timeout as tx:
            #     LOGGER.warning("http timeout.", tx)
            #     status = LinkStatus.DOING
            except ProxyError as rx:
                LOGGER.warning("proxy error.", rx)
                status = LinkStatus.DOING
            except SSLError as se:
                LOGGER.warning("SSL error.", se)
                status = LinkStatus.UNREACHABLE
            except RetryError as rx:
                LOGGER.warning("retry error.", rx)
                status = LinkStatus.UNREACHABLE
            except BaseException as bx:
                LOGGER.warning("unexpect error.", bx)
                status = LinkStatus.UNREACHABLE
        return status, response

    @staticmethod
    def fetch_with_retry_json(url: str, params: {}, headers: {}):
        result = {}
        _, response = HttpUtils.fetch_with_retry(url, params, headers)
        if response is None:
            LOGGER.warning("url:{} not arrived.".format(url))
            return result

        if response.status_code != 200:
            LOGGER.warning("url:{} not arrived.".format(url))
            LOGGER.warning("request meet some issue: {}, msg:{}".format(response.status_code, response.text))
            return result

        return response.json()

    @staticmethod
    def fetch_with_retry_binary(url):
        return HttpUtils.fetch_with_retry(url, {}, {})
