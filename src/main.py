#!/usr/bin/env python
# -*- encoding: utf-8 -*-
import asyncio
import json
import os

from prisma import Prisma
from prisma.models import WhImage, Tag, Uploader

from com.log.log_print import Log
from com.common.http.http_utils import HttpUtils
from com.wh.core.wh_pic_manager import WhPicManager
from com.wh.db.wh_db_handler import WhDbHandler

# 日志初始化
Log.logging_init()

os.environ['NO_PROXY'] = 'localhost'


async def test() -> None:
    db_handler = WhDbHandler()
    await db_handler.connect()
    image = list()
    image.append(
        {
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

    tag = list()
    tag.append(
        {
            "id": 1,
            "name": "anime",
            "alias": "Chinese cartoons",
            "category_id": 1,
            "category": "Anime & Manga",
            "purity": "sfw",
            "created_at": "2015-01-16 02:06:45"
        }
    )
    tag.append(
        {
            "id": 2,
            "name": "people",
            "alias": "Chinese cartoons",
            "category_id": 1,
            "category": "Anime & Manga",
            "purity": "nsfw",
            "created_at": "2015-01-16 02:03:45"
        }
    )

    uploader = list()
    uploader.append(
        {
            "username": "test-user",
            "group": "User",
        }
    )

    await db_handler.batch_insert_images(image, tag, uploader)


async def main() -> None:
    manager = WhPicManager()
    await manager.connect()

    await manager.get_ims_sorting_by_data(is_stop_auto=False, is_download=False)


if __name__ == "__main__":
    # url = "https://wallhaven.cc/api/v1/search"
    # params = {
    #     "categories": 111,
    #     "purity": 111,
    #     "sorting": "date_added*",
    #     "order": "desc*",
    # }
    # HttpUtils.fetch_with_retry(url, params, {})
    asyncio.run(main())
