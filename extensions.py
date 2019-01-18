#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2017/11/28 下午4:57
# @Author : Matrix
# @Github : https://github.com/blackmatrix7/
# @Blog : http://www.cnblogs.com/blackmatrix/
# @File : extensions.py
# @Software: PyCharm
import logging
from dingtalk import DingTalkApp
from config import DingTalkConfig
from dingtalk import SessionManager

__author__ = 'blackmatrix'

class MySQLSessionManager(SessionManager):

    """
    一个简单实现的使用MySQL实现管理access token和jsapi ticket过期时间的例子

    SET NAMES utf8mb4;
    SET FOREIGN_KEY_CHECKS = 0;
    -- ----------------------------
    -- Table structure for dingtalk_cache
    -- ----------------------------
    DROP TABLE IF EXISTS `dingtalk_cache`;
    CREATE TABLE `dingtalk_cache` (
      `key` varchar(255) NOT NULL,
      `value` varchar(255) NOT NULL,
      `create_time` datetime NOT NULL ON UPDATE CURRENT_TIMESTAMP,
      `expire_time` datetime NOT NULL,
      PRIMARY KEY (`key`),
      KEY `row_id` (`key`,`value`,`create_time`,`expire_time`) USING BTREE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8;

    SET FOREIGN_KEY_CHECKS = 1;
    """

    def __init__(self, host, user, pass_, db, port=3306):
        import pymysql
        self.connection = pymysql.connect(host=host, port=port, user=user, password=pass_, db=db)
        self.connection.autocommit(True)

    def set(self, key, value, expires):
        cursor = self.connection.cursor()
        from datetime import datetime, timedelta
        create_time = datetime.now()
        expire_time = create_time + timedelta(seconds=expires)
        select_sql = 'SELECT sql_no_cache `key`, `value`, expire_time FROM dingtalk_cache WHERE `key`="{}"'.format(key)
        self.check_connect()
        data = cursor.execute(select_sql)
        # 因为数据库是varchar类型
        value = str(value)
        if data < 1:
            sql = 'INSERT INTO dingtalk_cache(`key`,`value`,create_time,expire_time) VALUES("{}","{}","{}","{}")'.format(
                key, value, create_time.strftime('%Y-%m-%d %H:%M:%S'), expire_time.strftime('%Y-%m-%d %H:%M:%S'))

        else:
            sql = 'UPDATE dingtalk_cache SET `value`="{}", create_time="{}", expire_time="{}" WHERE `key`="{}"'.format(
                value, create_time, expire_time, key)
        self.check_connect()
        cursor.execute(sql)
        cursor.close()

    def get(self, key):
        try:
            cursor = self.connection.cursor()
            from datetime import datetime
            select_sql = 'SELECT sql_no_cache `key`, `value`, expire_time FROM dingtalk_cache WHERE `key`="{}"'.format(key)
            self.check_connect()
            cursor.execute(select_sql)
            row = cursor.fetchone()
            key, value, expire_time = row
            now = datetime.now()
            if now >= expire_time:
                return None
            else:
                return value
        except TypeError:
            return None
        except Exception as ex:
            logging.error(ex)
            return None

    def delete(self, key):
        del_sql = 'DELETE FROM dingtalk_cache WHERE `key`="{}"'.format(key)
        cursor = self.connection.cursor()
        self.check_connect()
        cursor.execute(del_sql)
        cursor.close()

    def check_connect(self):
        try:
            self.connection.ping()
        except BaseException as ex:
            logging.error(ex)
            self.connection()

#  # 钉钉会话管理
#  # Mysql支持
#  session_manager = MySQLSessionManager(host=DingTalkConfig.DING_SESSION_HOST,
#                                       port=DingTalkConfig.DING_SESSION_PORT,
#                                       user=DingTalkConfig.DING_SESSION_USER,
#                                       pass_=DingTalkConfig.DING_SESSION_PASS,
#                                       db=DingTalkConfig.DING_SESSION_DB)

#  # Memcached支持
#  from memcache import Client
#  session_manager = Client(DingTalkConfig.CACHE_MEMCACHED_SERVERS)

# Redis支持
import redis
pool = redis.ConnectionPool(host=DingTalkConfig.CACHE_REDIS_SERVERS,
                            port=DingTalkConfig.CACHE_REDIS_PORT,
                            db=DingTalkConfig.CACHE_REDIS_DB)
session_manager = redis.Redis(connection_pool=pool)
