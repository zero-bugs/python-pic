#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
# @File        : pic_status.py
# @Author      : anonymous
# @Time        : 2024/9/28 22:47
# @Description :
"""
from enum import Enum


class ImageStatus(Enum):
    INITIAL = 0
    DOWNLOADING = 1
    DOWNLOADED = 2
    NOTFOUND = 3
