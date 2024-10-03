#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import logging.config as lc


class LogUtils:
    root_config = {
        "version": 1,
        "formatters": {
            "root_fmt": {
                "format": "%(asctime)s-%(name)s-%(levelname)s-line %(lineno)d-%(message)s",
                "datefmt":"%Y-%m-%dT%H:%M:%S%z"
            },
        },
        "handlers": {
            "root_handler": {
                "class": "logging.StreamHandler",
                "level": "DEBUG",
                "formatter": "root_fmt",
            },
        },
        "root": {
            "level": "DEBUG",
            "handlers": ["root_handler"],
        },
    }

    custom = {
        "version": 1,
        "formatters": {
            "standard_fmt": {
                "format": "%(asctime)s-%(name)s-%(levelname)s-line %(lineno)d-%(message)s",
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
                "level": "DEBUG",
                "formatter": "standard_fmt",
                "backupCount": 5,
                "maxBytes": 1048576,
                "encoding": "utf8",
                "filename": "D:/code/python-pic/log/app.log",
            },
        },
        "loggers": {
            "common": {
                "level": "INFO",
                "handlers": ["console", "file"],
            },
            "wh": {
                "level": "DEBUG",
                "handlers": ["console", "file"],
            },
        }
    }

    @staticmethod
    def logging_init():
        lc.dictConfig(LogUtils.root_config)
        lc.dictConfig(LogUtils.custom)
