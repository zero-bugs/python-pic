#!/usr/bin/env python
# -*- encoding: utf-8 -*-
from typing import Any

from prisma import Prisma
from prisma.models import WhImage, Uploader, Tag


class WhDbHandler:
    def __init__(self):
        self.prisma = Prisma(auto_register=True)

    async def init(self):
        await self.prisma.connect()

    async def batch_insert_images(self, images: list[dict[str, Any]], tags: list[dict[str, Any]], uploader: list[dict[str, Any]]):
        """
        插入图片，处理冲突。
        :param uploader:
        :param tags:
        :param images:
        :return:
        """

        if images is None:
            return 0

        img_create_list, img_update_list = self.handle_unique_insert(images)
        tag_create_list, tag_update_list = self.handle_unique_insert(tags)
        upd_create_list, upd_update_list = self.handle_unique_insert(uploader)

        with self.prisma.tx() as transaction:
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
                        "id": value.id
                    }
                )

            for value in tag_create_list:
                await Tag.prisma(transaction).update(
                    data=value,
                    where={
                        "id": value.id
                    }
                )

            for value in upd_create_list:
                await Uploader.prisma(transaction).update(
                    data=value,
                    where={
                        "username": value.username
                    }
                )


    def handle_unique_insert(self, images):
        create_images = list()
        update_images = list()
        if images is None:
            return create_images, update_images

        for image in images:
            result = WhImage.prisma().find_unique(
                where={
                    "id": image.id
                }
            )
            if result is None:
                create_images.append(image)
            else:
                if self.is_need_update(image, result):
                    update_images.append(image)
        return create_images, update_images

    async def batch_update_images_status(self, images: list[WhImage], status):
        """
        更新图片相关字段
        :param images:
        :param status:
        :return:
        """

        if images is None:
            return 0

        _, img_update_list = self.handle_unique_insert(images)

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
        return image.source != result.source or image.purity != result.purity or image.category != result.category or image.file_size != result.file_size or image.path != result.path
