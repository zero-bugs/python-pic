#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import os

class Utils:
    @staticmethod
    def get_json_file(path: str):
        if not os.path.exists(path):
