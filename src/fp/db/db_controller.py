#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
# @File        : db_controller.py
# @Author      : anonymous
# @Time        : 2024/10/5 21:35
# @Description :
"""
import logging
from typing import Any

from prisma import Prisma
from prisma.models import InventoryTbl, ArticleTbl, ImageTbl

LOGGER = logging.getLogger('common')

class FpDbController:
    def __init__(self):
        self.prisma = Prisma(auto_register=True)

    async def connect(self):
        await self.prisma.connect()

    async def release(self):
        await self.prisma.disconnect()

    async def batch_insert_table(self, inventories: list[dict[str, Any]], articles: list[dict[str, Any]],
                                 images: list[dict[str, Any]]):
        """
        插入图片，处理冲突。
        :param images:
        :param articles:
        :param inventories:
        :return:
        """

        if inventories is None:
            return 0

        inv_create_list, inv_update_list = await self.handle_unique_insert(InventoryTbl, inventories)
        article_create_list, article_update_list = await self.handle_unique_insert(ArticleTbl, articles)
        img_create_list, inv_update_list = await self.handle_unique_insert(ImageTbl, images)

        async with self.prisma.tx() as transaction:
            await InventoryTbl.prisma(transaction).create_many(
                data=inv_create_list
            )

            await ArticleTbl.prisma(transaction).create_many(
                data=article_create_list
            )

            await ImageTbl.prisma(transaction).create_many(
                data=img_create_list
            )

            for value in inv_update_list:
                await InventoryTbl.prisma(transaction).update(
                    data=value,
                    where={
                        "name": value["name"]
                    }
                )

            for value in article_update_list:
                await ArticleTbl.prisma(transaction).update(
                    data=value,
                    where={
                        "article_id": value["article_id"]
                    }
                )

            for value in inv_update_list:
                await ImageTbl.prisma(transaction).update(
                    data=value,
                    where={
                        "url": value["url"]
                    }
                )

    async def handle_unique_insert(self, table, entries):
        create_entries = list()
        update_entries = list()
        if entries is None:
            return create_entries, update_entries

        for entry in entries:
            result = None
            if table.__name__ == 'InventoryTbl':
                result = await InventoryTbl.prisma().find_first(
                    where={
                        "name": entry["name"]
                    }
                )
            elif table.__name__ == 'ArticleTbl':
                result = await ArticleTbl.prisma().find_first(
                    where={
                        "article_id": entry["article_id"]
                    }
                )
            elif table.__name__ == 'ImageTbl':
                result = await ImageTbl.prisma().find_first(
                    where={
                        "url": entry["url"]
                    }
                )
            else:
                LOGGER.warning("invalid input table", table)

            if result is None:
                create_entries.append(entry)
            else:
                update_entries.append(entry)
        return create_entries, update_entries

    async def list_inventories_by_condition(self, condition, take, skip):
        if condition is None:
            condition = {}

        return await InventoryTbl.prisma().find_many(
            take=take,
            skip=skip,
            where=condition,
            order={
                'name': 'asc'
            }
        )

    async def update_inventory_status(self, inventory, status):
        await InventoryTbl.prisma().update(
            data={
                "status": status
            },
            where={
                "name": inventory.name
            }
        )