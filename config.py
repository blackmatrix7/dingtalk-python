#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2017/11/28 下午4:57
# @Author : Matrix
# @Github : https://github.com/blackmatrix7/
# @Blog : http://www.cnblogs.com/blackmatrix/
# @File : config.py
# @Software: PyCharm
from toolkit.cmdline import cmdline
from toolkit.config import BaseConfig, get_current_config

__author__ = 'blackmatrix'


class CommonConfig(BaseConfig):

    DEBUG = True
    TESTING = True

    # Cache
    CACHE_MEMCACHED_SERVERS = ['127.0.0.1:11211']
    CACHE_KEY_PREFIX = 'default'

    # dingtalk
    DING_GET_ACCESS_TOKEN = 'https://oapi.dingtalk.com/gettoken'
    DING_GET_JSAPI_TICKET = 'https://oapi.dingtalk.com/get_jsapi_ticket'
    DING_GET_USER_LIST = 'https://oapi.dingtalk.com/user/simplelist'
    DING_GET_USER_INFO = 'https://oapi.dingtalk.com/user/getuserinfo'
    DING_GET_DEPARTMENTS = 'https://oapi.dingtalk.com/department/list'
    DING_METHODS_URL = 'https://eco.taobao.com/router/rest'
    DING_CORP_ID = None
    DING_CORP_SECRET = None


class DevConfig(CommonConfig):

    # Cache
    CACHE_MEMCACHED_SERVERS = ['127.0.0.1:11211']
    CACHE_KEY_PREFIX = 'dev'


default = CommonConfig()
devcfg = DevConfig()

configs = {'default': default,
           'devcfg': devcfg}

# 读取配置文件的名称，在具体的应用中，可以从环境变量、命令行参数等位置获取配置文件名称
config_name = cmdline.config

current_config = get_current_config(config_name)
