#!/usr/bin/env python
# -*- encoding: utf-8 -*-

class HttpUtils:
    @staticmethod
    def fetch_with_retry(url: str):
        """
        获取响应，有重试
        :param url:
        :return:
        """