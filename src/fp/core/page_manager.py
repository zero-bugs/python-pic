#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
# @File        : page_manager.py.py
# @Author      : anonymous
# @Time        : 2024/10/5 20:39
# @Description :
"""
import asyncio
import os
import time
from concurrent.futures import ThreadPoolExecutor

from loguru import logger
from playwright.async_api import async_playwright

from common.config.config_manager import ConfigManager
from common.constant.link_status import LinkStatus
from common.constant.resource_type import ResourceType
from common.http.http_utils import HttpUtils
from common.utils.file_utils import FileUtils
from fp.db.db_controller import FpDbController

LOGGER = logger.bind(module_name="fp")


class FpPageManager:
    """
    抓取图片的处理类
    """

    def __init__(self):
        self.db_handler = FpDbController()
        # 并发执行数
        self.concurrent_num = 5

        # 线程池没批提交的任务数
        self.batch_submit_num = 20

    async def connect(self):
        await self.db_handler.connect()

    async def release(self):
        await self.db_handler.release()

    async def get_all_actresses_list(self):
        playwright = await async_playwright().start()
        browser = await playwright.chromium.launch(headless=True, timeout=600000)
        page = await browser.new_page()
        await page.route(
            "**/*.{png,jpg,jpeg,gif,mp4,ts,m3u8}", lambda route: route.abort()
        )
        await page.goto(ConfigManager.get_fp_all_actress_list(), timeout=600000)
        letter_sections = await page.query_selector_all(".letter-section")

        for section in letter_sections:
            inventories = []
            targets = await section.query_selector_all("ul >> a")
            for target in targets:
                href = await target.get_attribute("href")
                name = await target.inner_text()

                inventories.append(
                    {"name": name.strip(), "url": href.strip(), "status": 0}
                )

            await self.db_handler.batch_insert_table(inventories, list(), list())
            LOGGER.info("batch insert actresses list count:{}".format(len(inventories)))
            inventories.clear()

        await browser.close()
        await playwright.stop()

    async def get_all_actresses_list_by_inventory(self):
        """
        根据清单找到所有article
        :return:
        """
        LOGGER.info("begin to find all articles by inventories.")

        playwright = await async_playwright().start()
        browser = await playwright.chromium.launch(headless=True, timeout=600000)
        page = await browser.new_page()
        await page.route(
            "**/*.{png,jpg,jpeg,gif,mp4,ts,m3u8}", lambda route: route.abort()
        )

        condition = {"status": {"in": [LinkStatus.INITIAL, LinkStatus.DOING]}}
        take = 100
        skip = 0
        while True:
            inventories = await self.db_handler.list_inventories_by_condition(
                condition, take, skip
            )
            skip = 1
            if inventories is None or len(inventories) == 0:
                break

            for inventory in inventories:
                if (
                    inventory.status != LinkStatus.INITIAL
                    and inventory.status != LinkStatus.DOING
                ):
                    continue
                current_url = inventory.url
                article_list = []

                # 考虑多page场景
                status = LinkStatus.DONE
                while True:
                    await page.goto(current_url, timeout=600000)
                    articles = await page.query_selector_all("article")
                    for article in articles:
                        LOGGER.info(
                            "begin to find article by url:{}".format(current_url)
                        )
                        article_id = await article.get_attribute("id")
                        url_element = await article.query_selector(".entry-title a")
                        if url_element is None:
                            await self.db_handler.update_inventory_status(
                                inventory, LinkStatus.NOTFOUND
                            )
                            LOGGER.warning(
                                "actress:{} link:{} not found.".format(
                                    inventory.name, current_url
                                )
                            )
                            status = LinkStatus.NOTFOUND
                            break

                        url = await url_element.get_attribute("href")
                        title = await url_element.inner_text()
                        summary_element = await article.query_selector(
                            ".entry-content >> p"
                        )
                        summary = await summary_element.inner_text()

                        date_element = await article.query_selector(".entry-date")
                        created_at = await date_element.get_attribute("datetime")

                        article_list.append(
                            {
                                "article_id": article_id,
                                "name": inventory.name,
                                "title": title,
                                "url": url,
                                "summary": summary,
                                "created_at": created_at,
                                "status": 0,
                            }
                        )

                    # 处理下一页
                    next_page_element = await page.query_selector(".nav-previous a")
                    plain_next_page = ""
                    if next_page_element is not None:
                        plain_next_page = await next_page_element.inner_text()
                    if "Older posts" in plain_next_page:
                        current_url = await next_page_element.get_attribute("href")
                        LOGGER.info(
                            "article page more one, name:{}, page:{}".format(
                                inventory.name, current_url
                            )
                        )
                    else:
                        break

                await self.db_handler.batch_insert_table(list(), article_list, list())
                LOGGER.info(
                    "batch insert articles list count:{}".format(len(article_list))
                )
                article_list.clear()

                await self.db_handler.update_inventory_status(inventory, status)
                LOGGER.info(
                    "update inventory name:{} status from {} to {}".format(
                        inventory.name, inventory.status, status
                    )
                )
        # 关闭
        await browser.close()
        await playwright.stop()

    async def get_all_resources_list_by_article(self):
        """
        根据article找到所有图片的link
        :return:
        """
        LOGGER.info("begin to find all resources by article.")
        playwright = await async_playwright().start()
        browser = await playwright.chromium.launch(headless=True, timeout=600000)
        page = await browser.new_page()
        await page.route(
            "**/*.{png,jpg,jpeg,gif,mp4,ts,m3u8}", lambda route: route.abort()
        )

        condition = {"status": {"in": [LinkStatus.INITIAL, LinkStatus.DOING]}}
        take = 100
        skip = 0
        while True:
            articles = await self.db_handler.list_article_by_condition(
                condition, take, skip
            )
            skip = 1
            if articles is None or len(articles) == 0:
                break

            for article in articles:
                resource_list = []
                if article.status != LinkStatus.INITIAL:
                    continue
                current_url = article.url

                LOGGER.info(
                    "begin to find all resources by article:{}, article id:{}".format(
                        current_url, article.article_id
                    )
                )

                # 不需要考虑多page场景
                await page.goto(current_url, timeout=600000)
                post_element = await page.query_selector(
                    "#{}".format(article.article_id)
                )
                if post_element is None:
                    await self.db_handler.update_article_status(
                        article, LinkStatus.NOTFOUND
                    )
                    LOGGER.info("article url:{} not found.".format(current_url))
                    continue

                # 图片资源
                # 封面,封面link可能不是正文其中之一
                header_element = await post_element.query_selector(
                    ".entry-header >> img"
                )
                if header_element is not None:
                    src = await header_element.get_attribute("src")
                    srcset = await header_element.get_attribute("srcset")
                    url = self.get_url_from_src_set(src, srcset)
                    summary = await header_element.get_attribute("alt")
                    resource_list.append(
                        {
                            "url": url,
                            "article_id": article.article_id,
                            "summary": summary,
                            "type": ResourceType.FP_IMAGE,
                            "status": 0,
                        }
                    )

                # 内容
                img_element = await post_element.query_selector_all(
                    ".entry-content >> img"
                )
                LOGGER.info("begin to find image by url:{}".format(current_url))
                for img_element in img_element:
                    url = await img_element.get_attribute("src")
                    summary = await img_element.get_attribute("alt")
                    resource_list.append(
                        {
                            "url": url,
                            "article_id": article.article_id,
                            "summary": summary,
                            "type": ResourceType.FP_IMAGE,
                            "status": 0,
                        }
                    )

                # 视频资源
                video_element = await post_element.query_selector_all(
                    ".entry-content >> video"
                )
                LOGGER.info("begin to find video by url:{}".format(current_url))
                for video_element in video_element:
                    source_element = await video_element.query_selector("source")
                    url = await source_element.get_attribute("src")
                    summary = await source_element.get_attribute("alt")
                    resource_list.append(
                        {
                            "url": url,
                            "article_id": article.article_id,
                            "summary": summary,
                            "type": ResourceType.FP_VIDEO,
                            "status": 0,
                        }
                    )

                if len(resource_list) > 0:
                    await self.db_handler.batch_insert_table(
                        list(), list(), resource_list
                    )
                    LOGGER.info(
                        "batch insert images list count:{}".format(len(resource_list))
                    )
                else:
                    LOGGER.warning(
                        "find all resources by url:{} has no articles.".format(
                            current_url
                        )
                    )

                await self.db_handler.update_article_status(article, LinkStatus.DONE)
                LOGGER.info("article url:{} obtain success.".format(current_url))
                resource_list.clear()
            else:
                LOGGER.info(
                    "end to find to resources, articles num:{}, do next batch".format(
                        len(articles)
                    )
                )

        # 关闭
        await browser.close()
        await playwright.stop()

    def get_url_from_src_set(self, src, srcset):
        """
        样式：https://xxx/xxx-624x752.jpg 624w, https://xxx/xxx.jpg 1080w
        :param src:
        :param srcset:
        :return:
        """
        if srcset is None:
            return src

        srcset_list = srcset.split(",")
        if srcset_list is None or len(srcset_list) == 0:
            return src

        url = src
        pixel = 0
        for element in srcset_list:
            element_arr = element.strip().split(" ")
            if len(element_arr) == 2:
                url_temp = element_arr[0]
                if element_arr[1].replace("w", "").isdigit():
                    pixel_temp = int(element_arr[1].replace("w", ""))
                    if pixel_temp > pixel:
                        pixel = pixel_temp
                        url = url_temp
                else:
                    LOGGER.warning("src:{}, srcset:{} not normal.".format(src, srcset))
            else:
                LOGGER.warning(
                    "src:{}, srcset:{} not normal.element:{} can not split.".format(
                        src, srcset, element
                    )
                )
        return url

    async def download_all_resources_by_link(self):
        """
        根据image表中的link进行下载
        :return:
        """
        LOGGER.info("begin to execute download_all_resources_by_link")
        condition = {"status": {"in": [LinkStatus.INITIAL, LinkStatus.DOING]}}
        take = 200
        skip = 0
        download_path = ConfigManager.get_download_root_path()
        with ThreadPoolExecutor(max_workers=self.concurrent_num) as executor:
            while True:
                images = await self.db_handler.list_images(condition, take, skip)
                skip = 1
                if images is None or len(images) == 0:
                    break

                while len(images) > 0:
                    subtasks = []
                    current_num = min(self.batch_submit_num, len(images))
                    while len(subtasks) < current_num:
                        img = images.pop(0)
                        full_name = await self.get_image_full_name_obj(
                            download_path, img
                        )
                        loop = asyncio.get_running_loop()
                        subtasks.append(
                            loop.run_in_executor(
                                executor, self.download_one_image, img, full_name
                            )
                        )

                    start = time.time()
                    LOGGER.info("begin to execute thread num:{}".format(len(subtasks)))
                    done = await asyncio.gather(*subtasks)
                    LOGGER.info(
                        "end to execute thread num:{}, time:{:f}".format(
                            len(subtasks), time.time() - start
                        )
                    )
                    for rs in done:
                        status = rs[0]
                        image = rs[1]
                        if status != image.status:
                            await self.db_handler.update_image_status_for_obj(
                                image, status
                            )
                            LOGGER.info(
                                "update image url:{}, id:{}, status:{}".format(
                                    image.url, image.article_id, status
                                )
                            )
                    LOGGER.info("end to execute thread done num:{}".format(len(done)))

    async def get_image_full_name_obj(self, download_path, image):
        url = image.url
        if image.type == ResourceType.FP_IMAGE:
            name = url.split("/")[-1]
        elif image.type == ResourceType.FP_VIDEO:
            name = url.split("?")[0].split("/")[-1]
        else:
            LOGGER.warning("unknown resource type:{}".format(image.type))
            name = ""

        # 找到article
        article = await self.db_handler.find_article_by_id(image.article_id)
        if article is None:
            actress_name = "other"
            title = "unknown"
        else:
            actress_name = FileUtils.normalize_windows_path(article.name)
            title = FileUtils.normalize_windows_path(article.title)

        path = str(os.path.join(download_path, actress_name, title))
        if not os.path.exists(path):
            os.makedirs(path)
        full_path_name = os.path.join(path, name)
        LOGGER.debug("get full image path:{}".format(full_path_name))
        return full_path_name

    def download_one_image(self, image, image_name_full_name):
        """
        多线程时，将同步IO封装在单独线程中
        :param image: 图片
        :param image_name_full_name: 图片全名字
        :return:
        """
        status = image.status
        if image.status != LinkStatus.INITIAL and image.status != LinkStatus.DOING:
            return status, image

        LOGGER.info(
            "downloading image:{}, article id:{}".format(image.url, image.article_id)
        )
        status, response = HttpUtils.fetch_with_retry_binary(image.url)
        if response is None:
            return status, image

        LOGGER.info(
            "downloading image:{}, path:{} success".format(image.url, image.article_id)
        )

        if response.status_code == 200:
            # 不存在时或者大小为零，才会覆盖写
            if (
                not os.path.exists(image_name_full_name)
                or os.stat(image_name_full_name).st_size == 0
            ):
                LOGGER.info(
                    "write image:{} local, path:{} success".format(
                        image.url, image_name_full_name
                    )
                )
                with open(image_name_full_name, "wb") as f:
                    f.write(response.content)
                LOGGER.info(
                    "write image:{} local, path:{} success".format(
                        image.url, image_name_full_name
                    )
                )
            status = LinkStatus.DONE
            LOGGER.info(
                "update image:{}, id:{}, status:{}".format(
                    image.url, image.article_id, LinkStatus.DONE
                )
            )
        elif response.status_code == 404:
            status = LinkStatus.NOTFOUND
            LOGGER.info(
                "update image:{}, id:{}, status:{}, http code:{}".format(
                    image.url, image.article_id, status, response.status_code
                )
            )
        elif response.status_code == 302:
            status = LinkStatus.UNREACHABLE
            LOGGER.info(
                "update image:{}, id:{}, status:{}, http code:{}".format(
                    image.url, image.article_id, status, response.status_code
                )
            )
        elif response.status_code == 301:
            status = LinkStatus.UNREACHABLE
            LOGGER.info(
                "update image:{}, id:{}, status:{}, http code:{}".format(
                    image.url, image.article_id, status, response.status_code
                )
            )
        return status, image

    def run_in_thread_pool(self, image, full_name):
        """
        转换成同步函数
        :param image:
        :param full_name:
        :return:
        """
        new_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(new_loop)
        result = new_loop.run_until_complete(self.download_one_image(image, full_name))
        return result
