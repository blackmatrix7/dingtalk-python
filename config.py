#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2017/11/28 下午4:57
# @Author : Matrix
# @Github : https://github.com/blackmatrix7/
# @Blog : http://www.cnblogs.com/blackmatrix/
# @File : config.py
# @Software: PyCharm
import os
from toolkit.cmdline import cmdline
from toolkit.config import BaseConfig, get_current_config

__author__ = 'blackmatrix'


class CommonConfig(BaseConfig):

    DEBUG = True
    TESTING = True

    # Cache
    CACHE_MEMCACHED_SERVERS = ['127.0.0.1:11211']
    CACHE_KEY_PREFIX = 'default'


class DevConfig(CommonConfig):

    # Cache
    CACHE_MEMCACHED_SERVERS = ['127.0.0.1:11211']
    CACHE_KEY_PREFIX = 'dev'


default = CommonConfig()
devcfg = DevConfig()

configs = {'default': default,
           'devcfg': devcfg}

# 读取配置文件的名称，在具体的应用中，可以从环境变量、命令行参数等位置获取配置文件名称
config_name = 'default'

current_config = get_current_config(config_name)