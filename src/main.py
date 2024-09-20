#!/usr/bin/env python
# -*- encoding: utf-8 -*-
import asyncio

from prisma import Prisma
from prisma.models import WhImage, Tag, Uploader

from com.log.log_print import Log
from com.common.http.http_utils import HttpUtils

# 日志初始化
Log.logging_init()


async def main() -> None:
    prisma = Prisma(auto_register=True)
    await prisma.connect()

    async with prisma.tx() as transaction:
        await WhImage.prisma(transaction).create(
            data={
                "id": "94x38z",
                "views": 12,
                "favorites": 0,
                "source": "",
                "purity": "sfw",
                "category": "anime",
                "dimension_x": 6742,
                "dimension_y": 3534,
                "resolution": "6742x3534",
                "ratio": "1.91",
                "file_size": 5070446,
                "file_type": "image/jpeg",
                "created_at": "2018-10-31 01:23:10",
                "path": "https://w.wallhaven.cc/full/94/wallhaven-94x38z.jpg",
                "tags": "0",
                "uploader": "jim"
            }
        )

        await Tag.prisma(transaction).create_many(
            data=[
                {
                    "id": 1,
                    "name": "anime",
                    "alias": "Chinese cartoons",
                    "category_id": 1,
                    "category": "Anime & Manga",
                    "purity": "sfw",
                    "created_at": "2015-01-16 02:06:45"
                },
                {
                    "id": 2,
                    "name": "people",
                    "alias": "Chinese cartoons",
                    "category_id": 2,
                    "category": "Anime & Manga",
                    "purity": "sfw",
                    "created_at": "2015-01-18 02:06:45"
                }
            ]
        )

        await Uploader.prisma(transaction).create(
            data={
                "username": "test-user",
                "group": "User",
            }
        )


async def main1() -> None:
    db = Prisma()
    await db.connect()

    # write your queries here

    await db.disconnect()


if __name__ == "__main__":
    # url = "https://wallhaven.cc/api/v1/search"
    # params = {
    #     "categories": 111,
    #     "purity": 111,
    #     "sorting": "date_added*",
    #     "order": "desc*",
    # }
    # HttpUtils.fetch_with_retry(url, params, {})
    asyncio.run(main1())
