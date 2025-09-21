#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
# @File        : resource_download.py
# @Author      : anonymous
# @Time        : 2025/9/19 23:22
# @Description :
"""
import os

from loguru import logger

from common.http.http_utils import HttpUtils

LOGGER = logger.bind(module_name=__name__)

IMAGE_SETTING = {
    ".ai",
    ".apng",
    ".avif",
    ".bmp",
    ".cdr",
    ".dxf",
    ".eps",
    ".exif",
    ".fpx",
    ".gif",
    ".jfif",
    ".jp2",
    ".jpeg",
    ".jpg",
    ".pcd",
    ".pcx",
    ".pjp",
    ".pjpeg",
    ".png",
    ".psd",
    ".raw",
    ".svg",
    ".svgz",
    ".tga",
    ".tif",
    ".tiff",
    ".ufo",
    ".webp",
    ".wmf",
    ".xbm",
}
VIDEO_SETTING = {
    ".avi",
    ".wmv",
    ".mpeg",
    ".mp4",
    ".m4v",
    ".mov",
    ".asf",
    ".flv",
    ".f4v",
    ".rmvb",
    ".rm",
    ".3gp",
    ".vob",
    ".ts",
    ".m3u8",
    ".mkv",
    ".webm",
    ".mpeg",
    ".ogg",
}
SCRIPT_CODE_SETTING = {".php", ".js", ".c", ".py", ".sh", "widget"}
EXCLUDED_RESOURCE_TYPES = {"stylesheet", "script", "image", "font", "video"}


class ResourceDownloadUtils:
    @staticmethod
    def download_image(url, name):
        """
        下载图片
        :param url: 图片link
        :param name: 图片保存地址全路径
        :return: None
        """
        if not os.path.exists(os.path.dirname(name)):
            os.makedirs(os.path.dirname(name), exist_ok=True)

        if os.path.exists(name):
            LOGGER.warning("url:{}, name:{} has existed.".format(url, name))
            return
        status, response = HttpUtils.fetch_with_retry_binary(url)
        if response is None:
            LOGGER.warning("image:{}, response is null.", url)
            return None

        LOGGER.info("downloading image id:{}, path:{}".format(url, name))
        if response.status_code == 200:
            with open(name, "wb") as f:
                f.write(response.content)
        elif response.status_code == 404:
            LOGGER.warning("url:{} not found".format(url))
        else:
            LOGGER.warning(
                "url:{} error with code:{}".format(url, response.status_code)
            )

    @staticmethod
    def pic_link_filter(pic: str):
        """
        judge link is picture or not
        :param pic:
        :return:
        """
        if not pic or pic.strip() == "":
            return False
        suffix = pic.lower().split(".")[-1]
        if ".%s" % suffix in IMAGE_SETTING:
            return True
        return False

    @staticmethod
    async def block_aggressively(route):
        if route.request.resource_type in EXCLUDED_RESOURCE_TYPES:
            await route.abort()
        elif any(route.request.url.lower().endswith(ext) for ext in VIDEO_SETTING):
            await route.abort()
        elif any(route.request.url.lower().endswith(ext) for ext in IMAGE_SETTING):
            await route.abort()
        elif any(
            route.request.url.lower().endswith(ext) for ext in SCRIPT_CODE_SETTING
        ):
            await route.abort()
        else:
            await route.continue_()
