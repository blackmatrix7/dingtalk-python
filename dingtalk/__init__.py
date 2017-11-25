#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2017/11/28 上午9:22
# @Author : Matrix
# @Github : https://github.com/blackmatrix7/
# @Blog : http://www.cnblogs.com/blackmatrix/
# @File : __init__.py.py
# @Software: PyCharm
from extensions import cache
from .authentication import get_access_token, get_jsapi_ticket, sign

__author__ = 'blackmatrix'


class DingTalkApp:

    def __init__(self, name, corp_id, corp_secret):
        self.name = name
        self.corp_id = corp_id
        self.corp_secret = corp_secret

    def get_access_token(self):
        """
        获取钉钉 access token，access token 7200秒过期
        在缓存中设置7000秒过期，每次过期会自动重新获取 access token
        :return:
        """
        key_name = '{}_access_token'.format(self.name)
        access_token_cache = cache.get(key_name)
        if access_token_cache:
            return access_token_cache
        else:
            resp = get_access_token(self.corp_id, self.corp_secret)
            access_token = resp['access_token']
            cache.set(key_name, access_token, 7000)
            return access_token

    @property
    def access_token(self):
        return self.get_access_token()

    def get_jsapi_ticket(self):
        key_name = '{}_jsapi_ticket'.format(self.name)
        jsapi_ticket_cache = cache.get(key_name)
        if jsapi_ticket_cache:
            return jsapi_ticket_cache
        else:
            resp = get_jsapi_ticket(self.access_token)
            ticket = resp['ticket']
            cache.set(key_name, ticket, 7000)
            return ticket

    @property
    def jsapi_ticket(self):
        return self.get_jsapi_ticket()

    @staticmethod
    def sign(ticket, nonce_str, time_stamp, url):
        """
        计算签名信息
        :param ticket:
        :param nonce_str:
        :param time_stamp:
        :param url:
        :return:
        """
        return sign(ticket, nonce_str, time_stamp, url)

if __name__ == '__main__':
    pass
