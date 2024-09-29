#!/usr/bin/env python
# -*- encoding: utf-8 -*-
import logging
import os
import time

import requests
from prisma.models import WhImage
from requests import Timeout
from requests.adapters import HTTPAdapter
from requests.exceptions import RetryError
from urllib3 import Retry

from common.http.http_utils import HttpUtils
from common.config.config_manager import ConfigManager
from common.utils.utils import Utils
from wh.core.pic_status import ImageStatus
from wh.db.wh_db_handler import WhDbHandler
from wh.meta.image_meta import ImageMeta

LOGGER = logging.getLogger(__name__)


class WhPicManager:
    def __init__(self):
        self.db_handler = WhDbHandler()
        self.api_key = ConfigManager.get_api_key()

    async def connect(self):
        await self.db_handler.connect()

    async def release(self):
        await self.db_handler.release()

    async def get_ims_sorting_by_date_api(self, is_stop_auto=True, is_download=True):
        """
        从当前时间向历史遍历，获取图片
        功能1：列举图片，同时下载；
        功能2： 列举图片，但不下载，只更新数据库；
        :param is_stop_auto:
        :param is_download:
        :return:
        """

        url = ConfigManager.get_wh_query_images_api()
        params = {
            "categories": "111",
            "purity": "100",
            "sorting": "date_added*",
            "order": "desc*",
            "apikey": self.api_key
        }
        headers = {}

        result = HttpUtils.fetch_with_retry(url, params=params, headers=headers)
        meta = result['meta']
        data = result['data']

        current_page = 0
        per_page = 0
        last_page = 0
        if meta is not None:
            last_page = meta['last_page']
            per_page = meta['per_page']

        images = self.get_images_from_resp(data)
        await self.db_handler.batch_insert_images(images, list(), list())
        if is_download:
            await self.download_wh_images(images)

        download_result = False
        while current_page < last_page:
            current_page += 1
            params['page'] = current_page

            result = HttpUtils.fetch_with_retry(url, params=params, headers=headers)
            data = result['data']

            images = self.get_images_from_resp(data)
            await self.db_handler.batch_insert_images(images, list(), list())
            if is_download:
                download_result = await self.download_wh_images(images)

            # 所有图片都无需下载时，不继续遍历
            if download_result and is_stop_auto:
                LOGGER.warning("no need continue download, current page: %d, url: %s", current_page, url)
                break

            time.sleep(0.5)

    def get_images_from_resp(self, data: dict[str]):
        images = list()
        if isinstance(data, list):
            for item in data:
                images.append(ImageMeta.build_json_obj(item))
        else:
            images.append(ImageMeta.build_json_obj(data))
        return images

    async def download_wh_images(self, images):
        """
        下载图片
        :param images:
        :return: 是否都不需要下载
        """
        if images is None:
            return False

        download_path = str(os.path.join(ConfigManager.get_output_dir(), ConfigManager.get_type()))
        # 检查路径是否存在
        if not os.path.exists(download_path):
            os.makedirs(download_path, exist_ok=True)

        image_actual_no_need_dld = 0
        for image in images:
            # 检查图片是否存在
            image_name = image['id'] + self.get_pic_suffix(image['file_type'])

            image_full_path = os.path.join(download_path, image['category'], image['purity'], Utils.get_year_and_month_from_str(image['created_at']))
            if not os.path.exists(image_full_path):
                os.makedirs(image_full_path, exist_ok=True)
            image_name_full_path = os.path.join(image_full_path, image_name)
            if os.path.exists(image_name_full_path):
                image_actual_no_need_dld += 1
                continue

            is_exist = await self.db_handler.is_entry_exist(WhImage, image['id'])
            if is_exist:
                image_actual_no_need_dld += 1
                continue

            response = None
            with requests.Session() as session:
                retries = Retry(
                    total=10,
                    backoff_factor=0.5,
                    backoff_max=300,
                    status_forcelist=[429, 500, 503])
                session.mount(image['path'], HTTPAdapter(max_retries=retries))

                response = None
                try:
                    response = session.get(
                        image['path'],
                        verify=True,
                        timeout=(3, 10),
                        headers={
                            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                            'accept-encoding': 'gzip, deflate, br',
                            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36',
                        },
                        proxies=ConfigManager.get_proxy_config(),
                    )
                except Timeout as tx:
                    LOGGER.warning("http timeout.", tx)
                except RetryError as rx:
                    LOGGER.warning("retry error.", rx)
                except BaseException as bx:
                    LOGGER.warning("unexpect error.", bx)

                if response is None:
                    continue

                if response.status_code == 200:
                    with open(image_name_full_path, 'wb') as f:
                        f.write(response.content)
                    await self.db_handler.update_image_status(image, ImageStatus.DOWNLOADED)
                if response.status_code == 404:
                    await self.db_handler.update_image_status(image, ImageStatus.NOTFOUND)
                    LOGGER.warning("image not found. img:{}".format(image_name))
                    image_actual_no_need_dld += 1
        else:
            return image_actual_no_need_dld == len(images)


    def get_pic_suffix(self, extension):
        if extension is None:
            return ".jpg"

        if 'jpeg' in extension.lower() or 'jpg' in extension.lower():
            return '.jpg'
        elif 'png' in extension:
            return '.png'
        else:
            LOGGER.warning("pic suffix is not support. ", extension)
            return '.jpg'


    def backup_full_scan_and_download(self):
        """
        读取数据库中没有下载的链接并下载
        :return:
        """
