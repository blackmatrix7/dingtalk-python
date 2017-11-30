#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2017/11/28 上午9:22
# @Author : Matrix
# @Github : https://github.com/blackmatrix7/
# @Blog : http://www.cnblogs.com/blackmatrix/
# @File : __init__.py.py
# @Software: PyCharm
import json
from extensions import cache
from .foundation import get_timestamp
from .authentication import get_access_token, get_jsapi_ticket, sign
from .customers import get_corp_ext_list, add_corp_ext, get_label_groups

__author__ = 'blackmatrix'


def dingtalk(method_name):
    def wrapper(func):
        def _wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return _wrapper
    return wrapper


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

    @property
    def timestamp(self):
        return get_timestamp()

    def get_request_url(self, method, format_='json', v='2.0', simplify='false', partner_id=None):
        url = 'https://eco.taobao.com/router/rest?method={0}&session={1}&timestamp={2}&format={3}&v={4}'.format(
            method, self.access_token, self.timestamp, format_, v)
        if format_ == 'json':
            url = '{0}&simplify={1}'.format(url, simplify)
        if partner_id:
            url = '{0}&partner_id={1}'.format(url, partner_id)
        return url

    @dingtalk('dingtalk.corp.ext.listlabelgroups')
    def get_label_groups(self, size=20, offset=0):
        """
        获取系统标签
        :param size:
        :param offset:
        :return:
        """
        key_name = '{}_label_groups'.format(self.name)
        label_groups_cache = cache.get(key_name)
        if label_groups_cache:
            return label_groups_cache
        else:
            data = get_label_groups(access_token=self.access_token, size=size, offset=offset)
            data = json.loads(data['dingtalk_corp_ext_listlabelgroups_response']['result'])
            cache.set(key_name, data, 3600)
            return data

    @dingtalk('dingtalk.corp.ext.list')
    def get_ext_list(self):
        """
        获取外部联系人
        :return:
        """
        resp = get_corp_ext_list(self.access_token)
        result = json.loads(resp['dingtalk_corp_ext_list_response']['result'])
        return result

    @dingtalk('dingtalk.corp.ext.add')
    def add_corp_ext(self, contact):
        """
        获取外部联系人
        :return:
        """
        payload = {'contact': contact}
        resp = add_corp_ext(self.access_token, payload)
        return resp


if __name__ == '__main__':
    pass
