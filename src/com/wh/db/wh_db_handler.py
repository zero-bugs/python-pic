#!/usr/bin/env python
# -*- encoding: utf-8 -*-
import logging
from typing import Any

from prisma import Prisma
from prisma.models import WhImage, Uploader, Tag

LOGGER = logging.getLogger(__name__)

class WhDbHandler:
    def __init__(self):
        self.prisma = Prisma(auto_register=True)

    async def init(self):
        await self.prisma.connect()

    async def batch_insert_images(self, images: list[dict[str, Any]], tags: list[dict[str, Any]],
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
                data=img_update_list
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

            for value in tag_create_list:
                await Tag.prisma(transaction).update(
                    data=value,
                    where={
                        "id": value["id"]
                    }
                )

            for value in upd_create_list:
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
            result=None
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
                if self.is_need_update(entry, result):
                    update_entries.append(entry)
        return create_entries, update_entries

    async def batch_update_images_status(self, images: list[WhImage], status):
        """
        更新图片相关字段
        :param images:
        :param status:
        :return:
        """

        if images is None:
            return 0

        _, img_update_list = self.handle_unique_insert(WhImage, images)

        with self.prisma.tx() as transaction:
            for image in img_update_list:
                image.status = status
                await WhImage.prisma(transaction).update(
                    data=image,
                    where={
                        "id": image.id
                    }
                )

    def is_need_update(self, image, result):
        return image["source"] != result.source or image["purity"] != result.purity or image["category"] != result.category or image["file_size"] != result.file_size or image["path"] != result.path



