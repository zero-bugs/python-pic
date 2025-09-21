#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
# @File        : sis_page_manager.py
# @Author      : anonymous
# @Time        : 2025/5/31 15:51
# @Description :
"""
import os

from loguru import logger
from playwright.async_api import async_playwright

from plugins.sis001.sis_config import SisConstant
from plugins.sis001.sis_meta import SisMeta
from plugins.sis001.sis_utils import SisUtils

LOGGER = logger.bind(module_name="template1_get_all_link_by_start")


class SisPageManager:
    def __init__(self):
        self.all_links_current = set()
        self.all_links_used = set()
        self.all_images_downloaded = set()

    async def template_get_all_link_by_start_recursion(self, start_page):
        """
        通过起始页面信息找到接下来的页面
        :param start_page: html文件地址，非全量url
        :return: 文本和图片
        """
        self.all_links_current.add(start_page)

        playwright = await async_playwright().start()
        browser = await playwright.chromium.launch(headless=False, timeout=600000)
        page = await browser.new_page(ignore_https_errors=True)

        while len(self.all_links_current) > 0:
            current = self.all_links_current.pop()
            if current in self.all_links_used:
                continue

            page_address = SisConstant.HOST + current
            await page.route(
                "**/*.{png,jpg,jpeg,gif,mp4,ts,m3u8}", lambda route: route.abort()
            )
            await page.goto(page_address, timeout=30000)

            LOGGER.info("current page: {}".format(page_address))

            post_messages = await page.locator(".postmessage").all()
            if post_messages is None:
                continue

            for message in post_messages:
                sis_meta = SisMeta()
                title_loc = message.get_by_role("heading")
                if title_loc is None:
                    continue
                titles = await title_loc.all_inner_texts()
                for title in titles:
                    is_find = False
                    for key_words in SisConstant.KEY_WORD_LIST:
                        if title or title.find(key_words) != -1:
                            sis_meta.p_title = title.strip()
                            is_find = True
                            break
                    if is_find:
                        break

                post_mes_ids = await message.locator("div").all()
                if post_mes_ids is None:
                    continue
                for post_mes_id in post_mes_ids:
                    post_id = await post_mes_id.get_attribute("id")
                    if post_id is None or not post_id.startswith("postmessage_"):
                        continue

                    all_plain = await post_mes_id.inner_text()
                    all_plain = all_plain + "\n" + "page address: " + page_address

                    link_locs = await post_mes_id.get_by_role("link").all()
                    for link_loc in link_locs:
                        link = await link_loc.get_attribute("href")
                        if not link:
                            continue
                        if link.startswith("https"):
                            sis_meta.p_address.append(link.strip())
                            all_plain = (
                                all_plain
                                + "\n"
                                + "link: "
                                + "; ".join(sis_meta.p_address)
                            )
                        elif link.startswith("thread-"):
                            self.all_links_current.add(link.strip())

                    img_locs = await post_mes_id.locator("img").all()
                    images = list()
                    for img_loc in img_locs:
                        # 根据img下方的规律判断是否结束
                        img = await img_loc.get_attribute("src")
                        attach_obj = await img_loc.locator("css= + .t_attach").all()
                        if attach_obj is None or len(attach_obj) == 0:
                            continue

                        # 如果又分隔信息才会去获取图片链接
                        if not img:
                            continue
                        images.append(img)

                    img_path = os.path.join(
                        SisConstant.DOWNLOAD_DIR,
                        SisUtils.validate_title(sis_meta.p_title),
                    )
                    if not os.path.exists(img_path):
                        os.makedirs(img_path)

                    all_plain = all_plain + "\n"
                    all_plain = all_plain + "image list as below:" + "\n"
                    for img in images:
                        name = img.split("/")[-1]
                        if name in self.all_images_downloaded:
                            continue
                        img_full_name = os.path.join(img_path, name)

                        img_name = img
                        if not img.startswith("http"):
                            img_name = SisConstant.HOST + img
                        all_plain = all_plain + img_name + "\n"

                        SisUtils.download_image(img_name, img_full_name)
                        self.all_images_downloaded.add(name)

                    text_path = os.path.join(img_path, post_id + ".txt")
                    SisUtils.write_summary(all_plain, text_path)

                    break
            else:
                self.all_links_used.add(current)

        await browser.close()
        await playwright.stop()
