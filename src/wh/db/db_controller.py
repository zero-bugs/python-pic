#!/usr/bin/env python
# -*- encoding: utf-8 -*-
import logging
from typing import Any

from prisma import Prisma
from prisma.models import WhImage, Uploader, Tag

LOGGER = logging.getLogger('common')

class WhDbController:
    def __init__(self):
        self.prisma = Prisma(auto_register=True)

    async def connect(self):
        await self.prisma.connect()

    async def release(self):
        await self.prisma.disconnect()

    async def batch_insert_table(self, images: list[dict[str, Any]], tags: list[dict[str, Any]],
                                 uploader: list[dict[str, Any]]):
        """
        插入图片，处理冲突。
        :param uploader:
        :param tags:
        :param images:
        :return:
        """

        if images is None:
            return 0

        img_create_list, img_update_list = await self.handle_unique_insert(WhImage, images)
        tag_create_list, tag_update_list = await self.handle_unique_insert(Tag, tags)
        upd_create_list, upd_update_list = await self.handle_unique_insert(Uploader, uploader)

        async with self.prisma.tx() as transaction:
            await WhImage.prisma(transaction).create_many(
                data=img_create_list
            )

            await Tag.prisma(transaction).create_many(
                data=tag_create_list
            )

            await Uploader.prisma(transaction).create_many(
                data=upd_create_list
            )

            for value in img_update_list:
                await WhImage.prisma(transaction).update(
                    data=value,
                    where={
                        "id": value["id"]
                    }
                )

            for value in tag_update_list:
                await Tag.prisma(transaction).update(
                    data=value,
                    where={
                        "id": value["id"]
                    }
                )

            for value in upd_update_list:
                await Uploader.prisma(transaction).update(
                    data=value,
                    where={
                        "username": value["username"]
                    }
                )

    async def handle_unique_insert(self, table, entries):
        create_entries = list()
        update_entries = list()
        if entries is None:
            return create_entries, update_entries

        for entry in entries:
            result = None
            if table.__name__ == 'WhImage':
                result = await WhImage.prisma().find_first(
                    where={
                        "id": entry["id"]
                    }
                )
            elif table.__name__ == 'Tag':
                result = await Tag.prisma().find_first(
                    where={
                        "id": entry["id"]
                    }
                )
            elif table.__name__ == 'Uploader':
                result = await Uploader.prisma().find_first(
                    where={
                        "username": entry["username"]
                    }
                )
            else:
                LOGGER.warning("invalid input table", table)

            if result is None:
                create_entries.append(entry)
            else:
                if WhDbController.is_need_update(table, entry, result):
                    update_entries.append(entry)
        return create_entries, update_entries

    async def find_one_entry(self, table, key):
        if table.__name__ == 'WhImage':
            result = await WhImage.prisma().find_first(
                where={
                    "id": key
                }
            )
            return result
        elif table.__name__ == 'Tag':
            result = await Tag.prisma().find_first(
                where={
                    "id": key
                }
            )
            return result
        elif table.__name__ == 'Uploader':
            result = await Uploader.prisma().find_first(
                where={
                    "username": key
                }
            )
            return result
        else:
            LOGGER.warning("invalid input table", table)
            return None

    async def update_image_status(self, image, status):
        await WhImage.prisma().update(
            data={
                "status": status
            },
            where={
                "id": image.id
            }
        )

    async def list_images_by_date(self, condition=None, take=10, skip=0):
        if condition is None:
            condition = {}

        return await WhImage.prisma().find_many(
            take=take,
            skip=skip,
            where=condition,
            order={
                'created_at': 'desc'
            }
        )

    @staticmethod
    def is_need_update(table, entry, result):
        if table.__name__ == 'WhImage':
            return entry["created_at"] != result.created_at
        elif table.__name__ == 'Tag':
            return entry["created_at"] != result.created_at
        elif table.__name__ == 'Uploader':
            return entry["username"] != result.username or entry["group"] != result.group
        else:
            LOGGER.warning("invalid input table", table)