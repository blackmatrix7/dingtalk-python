#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2017/11/28 下午5:01
# @Author : Matrix
# @Github : https://github.com/blackmatrix7/
# @Blog : http://www.cnblogs.com/blackmatrix/
# @File : localconfig.py
# @Software: PyCharm
from config import CommonConfig

__author__ = 'blackmatrix'


class DevConfig(CommonConfig):

    # Cache
    CACHE_MEMCACHED_SERVERS = ['121.40.35.131:11211']
    CACHE_KEY_PREFIX = 'default'

    # DingTalk
    DING_CORP_ID = 'ding19cd2de441ef83f635c2f4657eb6378f'
    DING_CORP_SECRET = '3ab8Uk7WWhBMFaB7637YZF2EziCAlx6AunCox5GSJVFvfjtu35EJENSAUgWNEJys'


devcfg = DevConfig()

configs = {'default': devcfg,
           'devcfg': devcfg}