#!/usr/bin/env python
# -*- encoding: utf-8 -*-
import os
import time

from loguru import logger
from prisma.models import WhImage

from common.config.config_manager import ConfigManager
from common.constant.link_status import LinkStatus
from common.http.http_utils import HttpUtils
from common.utils.config_utils import ConfigUtils
from wh.db.db_controller import WhDbController
from wh.meta.image_meta import ImageMeta

LOGGER = logger.bind(module_name="wh")


class WhPicManager:
    def __init__(self):
        self.db_handler = WhDbController()
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

        url = ConfigManager.get_query_images_api()
        params = {
            "categories": "111",
            "purity": "011",
            "sorting": "date_added",
            "order": "desc",
            "apikey": self.api_key,
        }
        headers = {}
        result = HttpUtils.fetch_with_retry_json(url, params=params, headers=headers)
        if result is {}:
            return None

        meta = result["meta"]
        last_page = 0
        if meta is not None:
            last_page = meta["last_page"]

        LOGGER.info(f"meta info, meta:{meta}.")

        download_result = False
        current_page = 0
        while current_page < last_page:
            current_page += 1
            params["page"] = current_page

            LOGGER.info(f"current link:{url}, page:{current_page}")

            result = HttpUtils.fetch_with_retry_json(
                url, params=params, headers=headers
            )
            data = result["data"]

            images = self.get_images_from_resp(data)
            await self.db_handler.batch_insert_table(images, list(), list())
            if is_download:
                download_result = await self.download_wh_images(images)

            # 所有图片都无需下载时，不继续遍历
            if download_result and is_stop_auto:
                LOGGER.warning(f"no need continue download, current page: {current_page}, url: {url}")
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

        download_path = ConfigManager.get_download_root_path()

        image_actual_no_need_dld = 0
        for image in images:
            if image["purity"] != "nsfw" and image["purity"] != "sketchy":
                LOGGER.warning(f"image:{image["id"]} wrong purity:{image["purity"]}.")
                continue

            # 检查图片数据库是否存在
            result = await self.db_handler.find_one_entry(WhImage, image["id"])
            if result is not None and result.status != LinkStatus.INITIAL:
                LOGGER.warning(f"image:{image["id"]} has in db.")
                image_actual_no_need_dld += 1
                continue

            # 检查图片本地是否存在
            image_name, image_name_full_path = self.get_image_full_path_dict(
                download_path, image
            )
            if os.path.exists(image_name_full_path):
                LOGGER.warning(
                    "image:{} has in local:{}.", image["id"], image_name_full_path
                )
                image_actual_no_need_dld += 1
                continue

            status, response = HttpUtils.fetch_with_retry_binary(image["path"])
            if response is None:
                await self.db_handler.update_image_status_for_dict(image, status)
                LOGGER.warning(f"image:{image["id"]} with url:{image["path"]} response is null.")
                continue

            LOGGER.info(f"downloading image id:{image["id"]}, url:{image["path"]}, path:{image_name_full_path}")
            if response.status_code == 200:
                with open(image_name_full_path, "wb") as f:
                    f.write(response.content)
                await self.db_handler.update_image_status_for_dict(
                    image, LinkStatus.DONE
                )
            if response.status_code == 404:
                await self.db_handler.update_image_status_for_dict(
                    image, LinkStatus.NOTFOUND
                )
                LOGGER.warning(f"image not found. image id:{image["id"]}, url:{image["path"]}")
        else:
            LOGGER.info(f"the count of image which do not need download is: {image_actual_no_need_dld}, but all list is: {len(images)}")
            return image_actual_no_need_dld == len(images)

    def get_pic_suffix(self, extension):
        if extension is None:
            return ".jpg"

        if "jpeg" in extension.lower() or "jpg" in extension.lower():
            return ".jpg"
        elif "png" in extension:
            return ".png"
        else:
            LOGGER.warning(f"pic suffix:{extension} is not support")
            return ".jpg"

    async def background_full_scan_and_download(self):
        """
        读取数据库中没有下载的链接并下载
        :return:
        """
        LOGGER.info("begin to execute backup_full_scan_and_download")
        condition = {"OR": [{"purity": "nsfw"}, {"purity": "sketchy"}]}
        take = 5000
        skip = 0
        download_path = ConfigManager.get_download_root_path()
        while True:
            images = await self.db_handler.list_images_by_date(condition, take, skip)
            skip = 1
            if images is None or len(images) == 0:
                break
            skip += len(images)

            for image in images:
                if (
                    image.status != LinkStatus.INITIAL
                    and image.status != LinkStatus.DOING
                ):
                    continue

                LOGGER.info(f"downloading image:{image.id}, path:{image.path}")
                status, response = HttpUtils.fetch_with_retry_binary(image.path)
                if response is None:
                    await self.db_handler.update_image_status_for_obj(image, status)
                    continue

                LOGGER.info(f"downloading image:{image.id}, path:{image.path} success")

                if response.status_code == 200:
                    _, image_name_full_path = self.get_image_full_name_obj(
                        download_path, image
                    )
                    if not os.path.exists(image_name_full_path):
                        with open(image_name_full_path, "wb") as f:
                            f.write(response.content)
                        LOGGER.info("write image:{image.id} local, path:{image.path} success")
                    await self.db_handler.update_image_status_for_obj(
                        image, LinkStatus.DONE
                    )
                    LOGGER.info(f"update image:{image.id}, status:{LinkStatus.DONE}")
                elif response.status_code == 404:
                    await self.db_handler.update_image_status_for_obj(
                        image, LinkStatus.NOTFOUND
                    )
                    LOGGER.info(f"update image:{image.id}, status:{LinkStatus.NOTFOUND}")

    def get_image_full_path_dict(self, download_path, image):
        image_name = image["id"] + self.get_pic_suffix(image["file_type"])
        image_full_path = str(
            os.path.join(
                download_path,
                image["category"],
                image["purity"],
                ConfigUtils.get_year_and_month_from_str(image["created_at"]),
            )
        )
        if not os.path.exists(image_full_path):
            os.makedirs(image_full_path, exist_ok=True)
        image_name_full_path = os.path.join(image_full_path, image_name)
        return image_name, image_name_full_path

    def get_image_full_name_obj(self, download_path, image):
        image_name = image.id + self.get_pic_suffix(image.file_type)
        image_full_path = str(
            os.path.join(
                download_path,
                image.category,
                image.purity,
                ConfigUtils.get_year_and_month_from_str(image.created_at),
            )
        )
        if not os.path.exists(image_full_path):
            os.makedirs(image_full_path, exist_ok=True)
        image_name_full_path = os.path.join(image_full_path, image_name)
        return image_name, image_name_full_path
