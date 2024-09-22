#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from prisma import Prisma
from prisma.models import WhImage, Uploader, Tag


class WhDbHandler:
    def __init__(self):
        self.db_handler = WhDbHandler()
        self.prisma = Prisma(auto_register=True)

    async def init(self):
        await self.prisma.connect()

    def batch_insert_images(self, images: list[WhImage], tags: list[Tag], uploader: list[Uploader]):
        """

        :param uploader:
        :param tags:
        :param images:
        :return:
        """

        if images is None:
            return 0

        create_images = list(WhImage)
        update_images = list(WhImage)
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

    def batch_update_images(self, images: list[WhImage], status):
        """

        :param images:
        :param status:
        :return:
        """

        if images is None:
            return 0

        update_images = list(WhImage)
        for image in images:
            result = WhImage.prisma().find_unique(
                where={
                    "id": image.id
                }
            )

            if result:
                update_images.append(image)

        async with self.prisma.tx() as transaction:
            for image in update_images:
                WhImage.prisma(transaction).update(
                    data=image,
                    where={
                        "id": image.id
                    }
                )

    def is_need_update(self, image, result):
        return image.source != result.source or image.purity != result.purity or image.category != result.category or image.file_size != result.file_size or image.path != result.path
