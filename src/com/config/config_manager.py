#!/usr/bin/env python
# -*- encoding: utf-8 -*-
from src.com.common.utils.utils import Utils


class ConfigManager:
    @staticmethod
    def get_proxy_config():
        return Utils.read_json_file('./config/proxy.json')

    @staticmethod
    def get_api_key():
        jconfig = Utils.read_json_file('./config/app_config.json')
        return jconfig['apikey']

    @staticmethod
    def get_output_dir():
        jconfig = Utils.read_json_file('./config/app_config.json')
        return jconfig['result']

    @staticmethod
    def get_wh_query_images_api():
        jconfig = Utils.read_json_file('./config/app_config.json')
        protocol = jconfig['protocol']
        host = jconfig['host']
        uri = jconfig['QUERY_LIST_IMAGES']
        return "{}://{}/{}".format(protocol, host, uri)
