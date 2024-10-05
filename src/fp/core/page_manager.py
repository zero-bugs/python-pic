#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
# @File        : page_manager.py.py
# @Author      : anonymous
# @Time        : 2024/10/5 20:39
# @Description :
"""

from playwright.async_api import async_playwright

from common.config.config_manager import ConfigManager
from common.config.link_status import LinkStatus
from fp.db.db_controller import FpDbController, LOGGER


class FpPageManager:
    """
    抓取图片的处理类
    """

    def __init__(self):
        self.db_handler = FpDbController()

    async def connect(self):
        await self.db_handler.connect()

    async def release(self):
        await self.db_handler.release()

    async def get_all_actresses_list(self):
        playwright = await async_playwright().start()
        browser = await playwright.chromium.launch(headless=False, timeout=600000)
        page = await browser.new_page()
        await page.route("**/*.{png,jpg,jpeg,gif,mp4,ts,m3u8}", lambda route: route.abort())
        await page.goto(ConfigManager.get_fp_all_actress_list(), timeout=600000)
        letter_sections = await page.query_selector_all(".letter-section")

        inventories = []
        for section in letter_sections:
            targets = await section.query_selector_all('ul >> a')
            for target in targets:
                href = await target.get_attribute('href')
                name = await target.inner_text()

                inventories.append({
                    "name": name.strip(),
                    "url": href.strip(),
                    "status": 0
                })

                if len(inventories) % 500 == 0:
                    await self.db_handler.batch_insert_table(inventories, list(), list())
                    LOGGER.info("batch insert actresses list count:500")
                    inventories.clear()
        else:
            if len(inventories) > 0:
                await self.db_handler.batch_insert_table(inventories, list(), list())
                LOGGER.info("batch insert actresses list count:%d", len(inventories))
                inventories.clear()
        await browser.close()
        await playwright.stop()

    async def get_all_actresses_list_by_inventory(self):
        """
        根据清单找到所有article
        :return:
        """
        LOGGER.info("begin to find all articles by inventories.")
        condition = {}
        take = 100
        skip = 0

        playwright = await async_playwright().start()
        browser = await playwright.chromium.launch(headless=False, timeout=600000)
        page = await browser.new_page()
        await page.route("**/*.{png,jpg,jpeg,gif,mp4,ts,m3u8}", lambda route: route.abort())

        article_list = []
        while True:
            inventories = await self.db_handler.list_inventories_by_condition(condition, take, skip)
            if inventories is None or len(inventories) == 0:
                break
            skip += len(inventories)

            for inventory in inventories:
                if inventory.status != LinkStatus.INITIAL:
                    continue
                current_url = inventory.url
                while True:
                    await page.goto(current_url, timeout=600000)
                    articles = await page.query_selector_all('article')
                    for article in articles:
                        LOGGER.info("begin to find article by url:%s", current_url)
                        article_id = await article.get_attribute('id')
                        url_element = await article.query_selector('.entry-title a')
                        if url_element is None:
                            await self.db_handler.update_inventory_status(inventory, LinkStatus.NOTFOUND)
                            continue
                        url = await url_element.get_attribute('href')
                        title = await url_element.inner_text()
                        summary_element = await article.query_selector('.entry-content >> p')
                        summary = await summary_element.inner_text()

                        date_element = await article.query_selector('.entry-date')
                        created_at = await date_element.get_attribute('datetime')

                        article_list.append({
                            "article_id": article_id,
                            "name": inventory.name,
                            "title": title,
                            "url": url,
                            "summary": summary,
                            "created_at": created_at,
                            "status": 0,
                        })

                        if len(article_list) % 100:
                            await self.db_handler.batch_insert_table(list(), article_list, list())
                            LOGGER.info("batch insert articles list count:100")
                            article_list.clear()

                    # 处理下一页
                    next_page_element = await page.query_selector('.nav-previous a')
                    plain_next_page = ""
                    if next_page_element is not None:
                        plain_next_page = await next_page_element.inner_text()
                    if "Older posts" in plain_next_page:
                        current_url = await next_page_element.get_attribute('href')
                        LOGGER.info("article page more one, name:%s, page:%s", inventory.name, current_url)
                    else:
                        break
                await self.db_handler.update_inventory_status(inventory, LinkStatus.DONE)
                LOGGER.info("update inventory name:%s status from %d to %d", inventory.name, inventory.status,
                            LinkStatus.DONE)
            else:
                if len(article_list) > 0:
                    await self.db_handler.batch_insert_table(article_list, article_list, list())
                    LOGGER.info("batch insert articles list count:%d", len(article_list))
                    article_list.clear()
            # 关闭
            await browser.close()
            await playwright.stop()
