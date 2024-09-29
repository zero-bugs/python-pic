#!/usr/bin/env python
# -*- encoding: utf-8 -*-
from common.utils.utils import Utils


class ImageMeta:
    def __init__(self):
        self.id = None
        self.views = 0
        self.favorites = 0
        self.source = None
        self.purity = None
        self.category = None
        self.dimension_x = 0
        self.dimension_y = 0
        self.resolution = None
        self.ratio = None
        self.file_size = 0
        self.file_type = None
        self.created_at = None
        self.path = None
        self.tags = None
        self.uploader = None
        self.status = 0

    @staticmethod
    def build_json_obj(item: dict[str]):
        if 'created_at' not in item:
            item['created_at'] = Utils.get_current_time()

        return {
            "id": item['id'],
            "views": item['views'],
            "favorites": item['favorites'],
            "source": item['source'],
            "purity": item['purity'],
            "category": item['category'],
            "dimension_x": item['dimension_x'],
            "dimension_y": item['dimension_y'],
            "resolution": item['resolution'],
            "ratio": item['ratio'],
            "file_size": item['file_size'],
            "file_type": item['file_type'],
            "created_at": item['created_at'],
            "path": item['path'],
            "status": 0,
        }
