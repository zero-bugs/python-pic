#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import requests
from loguru import logger
from requests import HTTPError
from requests.adapters import HTTPAdapter, Retry
from requests.exceptions import (
    RetryError,
    ProxyError,
    SSLError,
    ConnectTimeout,
    ReadTimeout,
    Timeout,
)

from common.config.config_manager import ConfigManager
from common.constant.link_status import LinkStatus

LOGGER = logger.bind(module_name="common")


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
                status_forcelist=[429, 500, 502, 503, 504],
            )
            session.mount(url, HTTPAdapter(max_retries=retries))

            if headers is None or headers is {}:
                headers = (
                    {
                        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                        "accept-encoding": "gzip, deflate, br",
                        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36",
                    },
                )

            try:
                response = session.get(
                    url,
                    verify=ConfigManager.ignore_ssl_cert(),
                    timeout=(3, 10),
                    params=params,
                    headers=headers,
                    allow_redirects=False,
                    proxies=ConfigManager.get_proxy_config(),
                )
            except HTTPError as he:
                LOGGER.warning("http error, url:{} not arrived.", url)
                LOGGER.exception(he)
                status = LinkStatus.DOING
            except ConnectTimeout as ce:
                LOGGER.warning("connect timeout, url:{} not arrived.", url)
                LOGGER.exception(ce)
                status = LinkStatus.DOING
            except ReadTimeout as re:
                LOGGER.warning("read timeout, url:{} not arrived.", url)
                LOGGER.exception(re)
                status = LinkStatus.DOING
            except Timeout as tx:
                LOGGER.warning("timeout, url:{} not arrived.", url)
                LOGGER.exception(tx)
                status = LinkStatus.DOING
            except ProxyError as rx:
                LOGGER.warning("proxy error, url:{} not arrived.", url)
                LOGGER.exception(rx)
                status = LinkStatus.UNREACHABLE
            except SSLError as se:
                LOGGER.warning("SSL error, url:{} not arrived.", url)
                LOGGER.exception(se)
                status = LinkStatus.UNREACHABLE
            except RetryError as rx:
                LOGGER.warning("retry error, url:{} not arrived.", url)
                LOGGER.exception(rx)
                status = LinkStatus.UNREACHABLE
            except ConnectionError as ce:
                LOGGER.warning("connection error, url:{} not arrived.", url)
                LOGGER.exception(ce)
                status = LinkStatus.UNREACHABLE
            except BaseException as bx:
                LOGGER.warning("unexpect error, url:{} not arrived.", url)
                LOGGER.exception(bx)
                status = LinkStatus.UNREACHABLE
        return status, response

    @staticmethod
    def fetch_with_retry_json(url: str, params: {}, headers: {}):
        result = {}
        _, response = HttpUtils.fetch_with_retry(url, params, headers)
        if response is None:
            LOGGER.warning("url:{} not arrived.", url)
            return result

        if response.status_code != 200:
            LOGGER.warning("url:{} not arrived.", url)
            LOGGER.warning("request meet some issue: {}, msg:{}", response.status_code, response.text)
            return result

        return response.json()

    @staticmethod
    def fetch_with_retry_binary(url):
        return HttpUtils.fetch_with_retry(url, {}, {})
