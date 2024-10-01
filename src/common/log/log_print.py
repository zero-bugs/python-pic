#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import logging.config
import os


class Log:
    @staticmethod
    def logging_init(path="../config/logging.ini", def_level=logging.INFO):
        if os.path.exists(path):
            logging.config.fileConfig(path)
        else:
            logging.basicConfig(level=def_level)
