#!/usr/bin/env python
# -*- encoding: utf-8 -*-
from src.com.log.log_print import Log
from src.com.common.http.http_utils import HttpUtils

# 日志初始化
Log.logging_init()

if __name__ == "__main__":
    url = "https://wallhaven.cc/api/v1/search"
    params = {
        "categories": 111,
        "purity": 111,
        "sorting": "date_added*",
        "order": "desc*",
    }
    HttpUtils.fetch_with_retry(url, params, {})
