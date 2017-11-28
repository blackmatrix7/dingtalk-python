#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2017/8/18 上午9:31
# @Author : Matrix
# @Github : https://github.com/blackmatrix7/
# @Blog : http://www.cnblogs.com/blackmatrix/
# @File : config.py
# @Software: PyCharm
import os

__author__ = 'blackmatrix'


class ConfigMixin:

    """
    Config混合类，支持部分dict协议，实现以类似操作dict的方式操作配置文件。
    """

    def __setattr__(self, key, value):
        raise AttributeError

    def __setitem__(self, key, value):
        raise AttributeError

    def __delitem__(self, key):
        raise AttributeError

    def __getitem__(self, item):
        try:
            return getattr(self, item)
        except AttributeError as ex:
            raise KeyError('{0} object has no key {1}'.format(self.__class__.__name__, item)) from ex

    def __iter__(self):
        return (k for k in dir(self) if k.upper() == k)

    def __contains__(self, key):
        return hasattr(self, key)

    def items(self):
        return {k: getattr(self, k, None) for k in dir(self) if k.upper() == k}.items()

    def get(self, item, value=None):
        return getattr(self, item, value)


class BaseConfig(ConfigMixin):
    """
    配置文件基类
    """
    # 项目路径
    PROJ_PATH = os.path.abspath('')


def get_current_config(config_name=None):
    """
    对本地配置文件的支持，当项目根目录存在localconfig.py文件时
    优先从localconfig.py中读取配置，如果不存在读取config.py的配置。
    localconfig.py 应该加入git的忽略文件
    :return:
    """
    # 读取配置文件的名称，在具体的应用中，可以从环境变量、命令行参数等位置获取配置文件名称
    config_name = config_name or 'default'
    try:
        from localconfig import configs
        current_config = configs[config_name]
    except ImportError:
        from config import configs
        current_config = configs[config_name]
    return current_config



