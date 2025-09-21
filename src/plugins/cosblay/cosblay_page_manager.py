#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
# @File        : sis_page_manager.py
# @Author      : anonymous
# @Time        : 2025/5/31 15:51
# @Description :
"""
import os
import random
import urllib.parse

from loguru import logger
from playwright.async_api import async_playwright

from common.config.config_manager import ConfigManager
from common.http.resource_download import ResourceDownloadUtils
from common.utils.common_utils import CommonUtils
from common.utils.file_utils import FileUtils
from plugins.cosblay.cosblay_config import CosBlayConstant

LOGGER = logger.bind(module_name=__name__)


class CosBlayPageManager:
    def __init__(self):
        self.host = CosBlayConstant.HOST_KR
        self.download_dir = CosBlayConstant.DOWNLOAD_DIR
        self.article = None
        self.title = None
        self.max_page = 1
        self.img_all_links = set()
        self.page_all_links = set()

    async def template_get_link_from_detail_page(self, start_page: str):
        """
        详细信息模板页面，通过起始页面信息找到接下来的页面
        :param start_page: html文件地址，非全量url
        :return: 文本和图片
        """

        await self.init_params(start_page)

        playwright = await async_playwright().start()
        browser = await playwright.chromium.launch(
            headless=True,
            timeout=600000,
            proxy=ConfigManager.get_proxy_config_for_playwright(),
        )
        page = await browser.new_page(ignore_https_errors=True)
        await page.route(lambda route: True, ResourceDownloadUtils.block_aggressively)

        is_first_page = True
        while True:
            LOGGER.info(f"begin to access:{start_page}")
            try:
                await page.goto(
                    start_page,
                    timeout=180000,
                    wait_until="domcontentloaded",
                    referer=CosBlayConstant.HOST_KR,
                )
            except Exception as e:
                LOGGER.warning(
                    f"access:{start_page} failed {e}, waiting 30s...",
                    exc_info=True,
                    stack_info=True,
                )
                CommonUtils.waiting_with_print(30)
                continue

            if is_first_page:
                await self.init_detail_page_meta(page, is_first_page)
                is_first_page = False

            is_fc_checked = True
            articles = await page.locator(
                ".site-content > .content-area > .site-main article > .inside-article > .entry-content"
            ).all()
            for article_val in articles:
                is_fc_checked = False
                links = await article_val.get_by_role("link").all()
                for link in links:
                    href = await link.get_attribute("href")
                    if ResourceDownloadUtils.pic_link_filter(href):
                        self.img_all_links.add(href)
                LOGGER.info(
                    "article:{}, picture count:{}.".format(
                        self.article, len(self.img_all_links)
                    )
                )

                await self.__download_all_link_by_serial()
                self.img_all_links.clear()

            # 如果流控了，继续使用同一个地址等待
            if await self.check_page_flow_control(page, is_fc_checked):
                continue

            # find next page
            next_page = await page.locator(
                ".site-content > .content-area > .site-main article > .inside-article > .entry-content .pgntn-page-pagination-block > .post-page-numbers"
            ).all()
            if not next_page or len(next_page) == 0:
                break

            next_add = None
            for n_page in next_page:
                href = await n_page.get_attribute("href")
                next_content = await n_page.inner_text()
                if "下一頁" in next_content:
                    next_add = href.strip()
                if next_add:
                    break

            # 没找到下一页，退出
            if next_add is None:
                break
            else:
                LOGGER.info(f"current page links:{start_page}, next page:{next_add}")
                start_page = next_add
                CommonUtils.waiting_with_print(random.randint(10, 30))

        await browser.close()
        await playwright.stop()

    async def init_detail_page_meta(self, page, is_first_time):
        if not is_first_time:
            return

        title = await page.locator(
            ".site-content > .content-area > .site-main article > .inside-article > .entry-header > .entry-title"
        ).inner_text()
        if title and title.strip() != "":
            self.title = title.strip()
        artile_meta = await page.locator(
            ".site-content > .content-area > .site-main article"
        ).all()
        if artile_meta:
            for meta in artile_meta:
                article_id = await meta.get_attribute("id")
                if article_id and article_id.startswith("post-"):
                    self.article = article_id
        LOGGER.info(f"host:{self.host}, title:{self.title}, article:{self.article}")

        if self.article is None or self.title is None:
            raise ValueError(f"article:{self.article} or title:{self.title} is empty")

    async def init_params(self, start_page):
        url = urllib.parse.urlparse(start_page)
        self.host = url.hostname
        self.download_dir = os.path.join(self.download_dir, self.host)
        if self.host is None or self.host == "":
            raise ValueError("host param is None")

    async def template_get_link_from_batch_page(
        self, start_page: str, keyword: str = None
    ):
        """
        列表显示模板，支持通过关键字搜索获取图片 或者 分类的链接
        :param keyword:
        :param start_page:
        :return:
        """

        await self.init_params(start_page)

        playwright = await async_playwright().start()
        browser = await playwright.chromium.launch(
            headless=False,
            timeout=600000,
            proxy=ConfigManager.get_proxy_config_for_playwright(),
        )
        page = await browser.new_page(ignore_https_errors=True)
        await page.route(lambda route: True, ResourceDownloadUtils.block_aggressively)

        start_address = f"{start_page}/?s={keyword}" if keyword else start_page

        while True:
            LOGGER.info("begin to access:{}".format(start_address))
            try:
                await page.goto(
                    start_address,
                    timeout=180000,
                    wait_until="domcontentloaded",
                    referer=CosBlayConstant.HOST_KR,
                )
            except Exception as e:
                LOGGER.warning(
                    f"access:{start_address} failed {e}, waiting 30s...",
                    exc_info=True,
                    stack_info=True,
                )
                CommonUtils.waiting_with_print(30)
                continue

            articles = await page.locator(
                ".site-content > .content-area > .site-main article > .inside-article > .post-image"
            ).all()

            is_article_checked = True
            for article in articles:
                is_article_checked = False
                article_links = await article.get_by_role("link").all()
                for link in article_links:
                    href = await link.get_attribute("href")
                    if href.startswith(start_page):
                        self.page_all_links.add(href)
                        LOGGER.info(f"target link:{href}")

            # 如果流控了，继续使用同一个地址等待
            if await self.check_page_flow_control(page, is_article_checked):
                continue

            # find next page
            next_page = await page.locator(
                ".site-content > .content-area > .site-main .next.page-numbers"
            ).all()
            if not next_page or len(next_page) == 0:
                break

            next_add = None
            for n_page in next_page:
                next_add = await n_page.get_attribute("href")
                next_add = (
                    None
                    if next_add is None or next_add.strip() == ""
                    else next_add.strip()
                )
                if next_add:
                    break

            # 没找到下一页，退出
            if next_add is None:
                break
            else:
                start_address = next_add
                CommonUtils.waiting_with_print(random.randint(10, 30))
            LOGGER.info(
                "current page links:{}, next page:{}".format(
                    len(self.page_all_links), start_address
                )
            )

        # 暂时打印出来
        LOGGER.info(
            f"begin to print links for main page:{start_page}, keyword{keyword}"
        )
        for link in self.page_all_links:
            LOGGER.info("page:{}".format(link))

        await browser.close()
        await playwright.stop()

    async def check_page_flow_control(self, page, is_force_checked=True):
        is_flow_control = False
        if is_force_checked:
            flow_control_page = await page.locator(
                "#error-page > .wp-die-message"
            ).all()
            if flow_control_page:
                for link in flow_control_page:
                    page_link = await link.inner_text()
                    if "60" in page_link:
                        LOGGER.warning("flow control checked, sleep 60s...")
                        CommonUtils.waiting_with_print(60)
                        is_flow_control = True
                        continue
        return is_flow_control

    async def __download_all_link_by_serial(self):
        if len(self.img_all_links) == 0:
            LOGGER.warning("title:{} has no links.".format(self.title))
            return
        if self.article is None:
            LOGGER.warning("title:{} has not been loaded.".format(self.title))
            return

        img_path = os.path.join(
            CosBlayConstant.DOWNLOAD_DIR,
            self.host,
            FileUtils.normalize_str(self.title),
            FileUtils.normalize_str(self.article),
        )

        for link in self.img_all_links:
            filename = link.split("/")[-1]
            file_full_path = os.path.join(f"%s" % img_path, filename)

            ResourceDownloadUtils.download_image(link, file_full_path)
