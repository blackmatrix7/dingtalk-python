#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2017/11/28 下午4:57
# @Author : Matrix
# @Github : https://github.com/blackmatrix7/
# @Blog : http://www.cnblogs.com/blackmatrix/
# @File : extensions.py
# @Software: PyCharm
import redis
from dingtalk import DingTalkApp
from config import current_config

__author__ = 'blackmatrix'


# 缓存，Memcached支持
from memcache import Client
cache = Client(current_config.CACHE_MEMCACHED_SERVERS)
# 缓存，Redis支持
# cache = redis.Redis(host=current_config.CACHE_REDIS_SERVERS,
#                     port=current_config.CACHE_REDIS_PORT,
#                     db=current_config.CACHE_REDIS_DB)

# 实例化一个钉钉的对象
# 这里为了测试方便，引入了之前写的config模块，本身SDK的使用不需要此模块
# 可以用类似的方式实例化：
# app = DingTalkApp(name='test', cache=cache,
#                   agent_id='152919534',
#                   corp_id='ding19cdf2s221ef83f635c2e4523eb3418f',
#                   corp_secret='3ab8Uk7Wef4ytgf7YZF2EziCAlx6AufdF3dFvfjtu3532FG3AUgWNEJys',
#                   aes_key='4g5j64qlyl3zvetqxz5jiocdr586fn2zvjpa8zls3ij')
dd_config = {'corp_id': current_config.DING_CORP_ID,
             'corp_secret': current_config.DING_CORP_SECRET,
             'agent_id': current_config.DING_AGENT_ID,
             'domain': 'test_domain',
             'aes_key': current_config.DING_AES_KEY,
             'callback_url': current_config.DING_CALLBACK}
app = DingTalkApp(name='test', cache=cache, **dd_config)
