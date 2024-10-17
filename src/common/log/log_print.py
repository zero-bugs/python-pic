#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import logging.config as lc
import sys

from loguru import logger


class LogUtils:
    root_config = {
        "version": 1,
        "formatters": {
            "root_fmt": {
                "format": "[%(asctime)s][%(name)s][%(levelname)s][line %(lineno)d]%(message)s",
                "datefmt": "%Y-%m-%dT%H:%M:%S%z"
            },
        },
        "handlers": {
            "root_handler": {
                "class": "logging.StreamHandler",
                "level": "INFO",
                "formatter": "root_fmt",
            },
        },
        "root": {
            "level": "WARNING",
            "handlers": ["root_handler"],
        },
    }

    custom = {
        "version": 1,
        "formatters": {
            "standard_fmt": {
                "format": "[%(asctime)s][%(name)s][%(levelname)s][line %(lineno)d]%(message)s",
                "datefmt": "%Y-%m-%dT%H:%M:%S%z"
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": "INFO",
                "formatter": "standard_fmt",
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "INFO",
                "formatter": "standard_fmt",
                "backupCount": 20,
                "maxBytes": 20485760,
                "encoding": "utf8",
                "filename": "D:/code/python-pic/log/app.log",
            },
        },
        "loggers": {
            "common": {
                "level": "INFO",
                "handlers": ["file"],
            },
            "wh": {
                "level": "INFO",
                "handlers": ["file"],
            },
            "fp": {
                "level": "INFO",
                "handlers": ["file"],
            },
        }
    }

    @staticmethod
    def logging_init():
        lc.dictConfig(LogUtils.root_config)
        lc.dictConfig(LogUtils.custom)

    @staticmethod
    def logging_init_loguru():
        logger.configure(handlers=[
            {
                "sink": sys.stdout,
                "format": "{time:YYYY-MM-DD HH:mm:ss.SSS}|<lvl>{level:8}</>|{name}:{module}:{line:4}|<cyan>mymodule</>| - <lvl>{message}</>",
                "colorize": True
            },
            {
                "sink": 'D:/code/python-pic/log/run.log',
                "format": "{time:YYYY-MM-DD HH:mm:ss.SSS}|<lvl>{level:8}</>|{name}:{module}:{line:4}|<cyan>mymodule</>| - <lvl>{message}</>",
                "colorize": False,
                "level": "INFO"
            }
        ])
        logger.add("run_{time}.log", rotation='100 MB', compression='gz', retention=10, enqueue=True)
