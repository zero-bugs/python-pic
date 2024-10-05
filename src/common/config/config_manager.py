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
    def get_proxy_config_for_pw():
        proxy_json = Utils.read_json_file('../config/proxy.json')
        if proxy_json and proxy_json['switch']:
            return {
                'server': proxy_json['http_proxy'],
                'bypass': "localhost, 127.0.0.1",
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
        jconfig = Utils.read_json_file('../config/api_list.json')
        wh_jconfig = jconfig[ConfigManager.get_type()]
        protocol = wh_jconfig['protocol']
        host = wh_jconfig['host']
        uri = wh_jconfig['QUERY_LIST_IMAGES']['uri']
        return "{}://{}{}".format(protocol, host, uri)

    @staticmethod
    def get_fp_all_actress_list():
        jconfig = Utils.read_json_file('../config/api_list.json')
        wh_jconfig = jconfig[ConfigManager.get_type()]
        protocol = wh_jconfig['protocol']
        host = wh_jconfig['host']
        uri = wh_jconfig['ALL_ACTRESSES_LIST']['uri']
        return "{}://{}{}".format(protocol, host, uri)
