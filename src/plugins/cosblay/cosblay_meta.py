#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
# @File        : sis_meta.py
# @Author      : anonymous
# @Time        : 2025/5/31 15:52
# @Description :
"""


class CosDetailPageMeta(object):
    def __init__(self):
        self.id = ""
        self.title = ""
        self.url = ""
        self.summary = ""
        self.img_list = dict()

    def __str__(self):
        return "|".join([self.id, self.title, self.url])


class CosBatchPageMeta(object):
    def __init__(self):
        self.title = ""
        self.name = ""
        self.cur_page = ""
        self.summary = ""
        self.page_links = dict()

    def __str__(self):
        return "|".join([self.title, self.name])
