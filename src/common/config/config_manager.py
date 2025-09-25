#!/usr/bin/env python
# -*- encoding: utf-8 -*-
import os

from common.utils.config_utils import ConfigUtils

ROOT_PATH = os.path.abspath(os.path.dirname(__file__))
PROJECT_PATH = os.path.abspath(os.path.join(ROOT_PATH, os.pardir, os.pardir, os.pardir))


class ConfigManager:
    @staticmethod
    def get_proxy_config():
        proxy_json = ConfigUtils.read_json_file(f"{PROJECT_PATH}/config/proxy.json")
        if proxy_json and proxy_json["switch"]:
            return {
                "http": proxy_json["http_proxy"],
                "https": proxy_json["https_proxy"],
            }
        else:
            return {}

    @staticmethod
    def get_proxy_config_for_playwright():
        proxy_json = ConfigUtils.read_json_file(f"{PROJECT_PATH}/config/proxy.json")
        if proxy_json and proxy_json["switch"]:
            return {
                "server": proxy_json["http_proxy"],
                "bypass": proxy_json["no_proxy"],
            }
        else:
            return None

    @staticmethod
    def get_proxy_config_for_pw():
        proxy_json = ConfigUtils.read_json_file(f"{PROJECT_PATH}/config/proxy.json")
        if proxy_json and proxy_json["switch"]:
            return {
                "server": proxy_json["http_proxy"],
                "bypass": "localhost, 127.0.0.1",
            }
        else:
            return {}

    @staticmethod
    def get_type():
        jconfig = ConfigUtils.read_json_file(f"{PROJECT_PATH}/config/app_config.json")
        return jconfig["type"]

    @staticmethod
    def get_output_dir():
        jconfig = ConfigUtils.read_json_file(f"{PROJECT_PATH}/config/app_config.json")
        return jconfig["path"]

    @staticmethod
    def ignore_ssl_cert():
        proxy_json = ConfigUtils.read_json_file(f"{PROJECT_PATH}/config/app_config.json")
        if proxy_json and proxy_json["ignore_ssl_cert"]:
            return True
        else:
            return False

    @staticmethod
    def get_api_key():
        jconfig = ConfigUtils.read_json_file(f"{PROJECT_PATH}/config/api_list.json")
        b_type = ConfigManager.get_type()
        return jconfig[b_type]["api_key"]

    @staticmethod
    def get_query_images_api():
        jconfig = ConfigUtils.read_json_file(f"{PROJECT_PATH}/config/api_list.json")
        wh_jconfig = jconfig[ConfigManager.get_type()]
        protocol = wh_jconfig["protocol"]
        host = wh_jconfig["host"]
        uri = wh_jconfig["QUERY_LIST_IMAGES"]["uri"]
        return f"{protocol}://{host}{uri}"

    @staticmethod
    def get_fp_all_actress_list():
        jconfig = ConfigUtils.read_json_file(f"{PROJECT_PATH}/config/api_list.json")
        wh_jconfig = jconfig[ConfigManager.get_type()]
        protocol = wh_jconfig["protocol"]
        host = wh_jconfig["host"]
        uri = wh_jconfig["ALL_ACTRESSES_LIST"]["uri"]
        return "{}://{}{}".format(protocol, host, uri)

    @staticmethod
    def get_download_root_path():
        download_path = str(
            os.path.join(ConfigManager.get_output_dir(), ConfigManager.get_type())
        )
        # 检查路径是否存在
        if not os.path.exists(download_path):
            os.makedirs(download_path, exist_ok=True)
        return download_path
