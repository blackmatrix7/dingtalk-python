#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2017/11/28 下午4:57
# @Author : Matrix
# @Github : https://github.com/blackmatrix7/
# @Blog : http://www.cnblogs.com/blackmatrix/
# @File : extensions.py
# @Software: PyCharm
from dingtalk import Cache
from dingtalk import DingTalkApp
from config import current_config

__author__ = 'blackmatrix'

"""
这里为了测试方便，引入了之前编写的config模块，本身SDK的使用不需要此模块。
类似current_config.DING_CORP_ID的操作，本质上是从配置文件中读取配置项的值。
实际的项目运用中，可以通过其他方式获取配置参数。
"""
CORP_ID = current_config.DING_CORP_ID
CORP_SECRET = current_config.DING_CORP_SECRET
AGENT_ID = current_config.DING_AGENT_ID
DOMAIN = current_config.DING_DOMAIN
AES_KEY = current_config.DING_AES_KEY
CALLBACK_URL = current_config.DING_CALLBACK


# 缓存，Memcached支持
from memcache import Client
cache = Client(current_config.CACHE_MEMCACHED_SERVERS)
# 缓存，Redis支持
# import redis
# cache = redis.Redis(host=current_config.CACHE_REDIS_SERVERS,
#                     port=current_config.CACHE_REDIS_PORT,
#                     db=current_config.CACHE_REDIS_DB)


# MySQL支持
class MySQLCache(Cache):

    def __init__(self):
        import pymysql
        host = current_config.CACHE_MYSQL_HOST
        port = current_config.CACHE_MYSQL_PORT
        user = current_config.CACHE_MYSQL_USER
        pass_ = current_config.CACHE_MYSQL_PASS
        db_name = current_config.CACHE_MYSQL_DB
        self.connection = pymysql.connect(host=host, port=port, user=user, password=pass_, db=db_name)
        self.cursor = self.connection.cursor()

    def set(self, key, value, expires):
        sql = 'INSERT INTO CacheData(key, value, expire_time) VALUES({}, {}, {})'.format(key, value, expires)
        self.cursor.execute(sql)
        self.connection.commit()
        
    def get(self, key):
        pass

    def delete(self, key):
        pass

# 实例化一个钉钉的对象
dd_config = {'corp_id': CORP_ID, 'corp_secret': CORP_SECRET, 'agent_id': AGENT_ID,
             'domain': DOMAIN, 'aes_key': AES_KEY, 'callback_url': CALLBACK_URL}
app = DingTalkApp(name='test', cache=cache, **dd_config)
