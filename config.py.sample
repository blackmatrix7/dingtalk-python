#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2017/11/28 下午4:57
# @Author : Matrix
# @Github : https://github.com/blackmatrix7/
# @Blog : http://www.cnblogs.com/blackmatrix/
# @File : config.py
# @Software: PyCharm
from toolkit.config import BaseConfig, get_current_config

__author__ = 'blackmatrix'


class CommonConfig(BaseConfig):

    # 日期格式配置
    DATE_FMT = '%Y-%m-%d'
    DATETIME_FMT = '%Y-%m-%d %H:%M:%S'

    # 钉钉会话存储，memcached、redis、mysql任选其一即可
    # memcached
    CACHE_MEMCACHED_SERVERS = ['127.0.0.1:11211']
    # redis
    CACHE_REDIS_SERVERS = '127.0.0.1'
    CACHE_REDIS_PORT = '6379'
    CACHE_REDIS_DB = 0
    # mysql
    DING_SESSION_HOST = '127.0.0.1'
    DING_SESSION_PORT = 3306
    DING_SESSION_USER = 'root'
    DING_SESSION_PASS = 'password'
    DING_SESSION_DB = 'DingTalkCache'

    # DingTalk的信息配置
    DING_DOMAIN = 'testdomain'
    DING_CORP_ID = None
    DING_CORP_SECRET = None
    DING_AGENT_ID = None
    DING_AES_KEY = None
    DING_CALLBACK = None  # 钉钉回调地址，必须返回含有success字符串的json格式


class DevConfig(CommonConfig):

    # 钉钉会话存储
    CACHE_MEMCACHED_SERVERS = ['127.0.0.1:11211']


default = CommonConfig()
devcfg = DevConfig()

configs = {'default': default,
           'devcfg': devcfg}

# 读取配置文件的名称，在具体的应用中，可以从环境变量、命令行参数等位置获取配置文件名称
config_name = 'default'

current_config = get_current_config(config_name)
