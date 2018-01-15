#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2017/11/28 下午4:57
# @Author : Matrix
# @Github : https://github.com/blackmatrix7/
# @Blog : http://www.cnblogs.com/blackmatrix/
# @File : extensions.py
# @Software: PyCharm
from memcache import Client
from config import current_config

__author__ = 'blackmatrix'


# 缓存
cache = Client(current_config.CACHE_MEMCACHED_SERVERS)
