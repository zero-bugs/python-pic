#!/usr/bin/env python
# -*- encoding: utf-8 -*-
from common.utils.utils import Utils


class ConfigManager:
    @staticmethod
    def get_proxy_config():
        proxy_json = Utils.read_json_file('../config/proxy.json')
        if proxy_json and proxy_json['switch']:
            return {
                'http': proxy_json['http_proxy'],
                'https': proxy_json['https_proxy'],
            }
        else:
            return {}

    @staticmethod
    def get_type():
        jconfig = Utils.read_json_file('../config/app_config.json')
        return jconfig['type']

    @staticmethod
    def get_api_key():
        jconfig = Utils.read_json_file('../config/app_config.json')
        return jconfig['apikey']

    @staticmethod
    def get_output_dir():
        jconfig = Utils.read_json_file('../config/app_config.json')
        return jconfig['path']

    @staticmethod
    def get_wh_query_images_api():
        jconfig = Utils.read_json_file('../config/wh_api_list.json')
        wh_jconfig = jconfig['wh']
        protocol = wh_jconfig['protocol']
        host = wh_jconfig['host']
        uri = wh_jconfig['QUERY_LIST_IMAGES']['uri']
        return "{}://{}{}".format(protocol, host, uri)
