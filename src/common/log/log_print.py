#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import logging.config as lc
import os
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
        current_working_directory = os.getcwd()
        log_path = os.path.join(current_working_directory, "..", "log")
        log_file = os.path.join(log_path, "run.log")
        archive_log_file = log_path + "/run_{time}.log"
        logger.configure(handlers=[
            {
                "sink": sys.stdout,
                "format": "{time:YYYY-MM-DD HH:mm:ss.SSS}|<lvl>{level:8}</>|{name}:{module}:{line:4}|<cyan>module</>| - <lvl>{message}</>",
                "colorize": True,
                "level": "INFO"
            },
            {
                "sink": log_file,
                "format": "{time:YYYY-MM-DD HH:mm:ss.SSS}|<lvl>{level:8}</>|{name}:{module}:{line:4}|<cyan>module</>| - <lvl>{message}</>",
                "colorize": False,
                "level": "INFO"
            }
        ])
        logger.add(archive_log_file, rotation='100 MB', compression='gz', retention=10, enqueue=True)
