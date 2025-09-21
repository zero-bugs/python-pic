#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
# @File        : object_print.py
# @Author      : anonymous
# @Time        : 2025/9/21 11:22
# @Description :
"""
from abc import abstractmethod, ABC


class ObjectPrint(ABC):
    @abstractmethod
    def obj_print(self) -> str:
        return self.__str__()

    @abstractmethod
    def custom_print(self):
        return self.__str__()
