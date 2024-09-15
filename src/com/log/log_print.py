#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import logging.config
import os
import yaml


class Log:
    @staticmethod
    def logging_init(path="./config/logging.yaml", def_level=logging.INFO):
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                config = yaml.load(f, Loader=yaml.FullLoader)
                logging.config.dictConfig(config)
        else:
            logging.basicConfig(level=def_level)


    @staticmethod
    def info(msg):
        logging.info(msg)