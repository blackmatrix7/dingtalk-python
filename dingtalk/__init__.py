#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2017/11/28 上午9:22
# @Author : Matrix
# @Github : https://github.com/blackmatrix7/
# @Blog : http://www.cnblogs.com/blackmatrix/
# @File : __init__.py.py
# @Software: PyCharm
import json
from .foundation import get_timestamp
from .contacts import get_dempartment_list, get_user_list
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

    def __init__(self, name, cache, corp_id, corp_secret):
        self.name = name
        self.cache = cache
        self.corp_id = corp_id
        self.corp_secret = corp_secret

    def get_access_token(self):
        """
        获取钉钉 access token，access token 7200秒过期
        在缓存中设置7000秒过期，每次过期会自动重新获取 access token
        :return:
        """
        key_name = '{}_access_token'.format(self.name)

        @self.cache.cached(key_name, 7000)
        def _get_access_token():
            resp = get_access_token(self.corp_id, self.corp_secret)
            access_token = resp['access_token']
            return access_token

        return _get_access_token()

    @property
    def access_token(self):
        return self.get_access_token()

    def get_jsapi_ticket(self):
        key_name = '{}_jsapi_ticket'.format(self.name)

        @self.cache.cached(key_name, 7000)
        def _get_jsapi_ticket():
            resp = get_jsapi_ticket(self.access_token)
            ticket = resp['ticket']
            return ticket

        return _get_jsapi_ticket()

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

    def get_user_list(self, department_id=None):
        data = get_user_list(self.access_token, department_id)
        user_list = data['userlist']
        return user_list

    def get_dempartment_list(self, id_=None):
        key_name = '{}_dept_list'.format(self.name)

        @self.cache.cached(key_name, 3600)
        def _get_dempartment_list(_id):
            data = get_dempartment_list(self.access_token, _id)
            depart_list = data['department']
            return depart_list

        return _get_dempartment_list(_id=id_)

    @dingtalk('dingtalk.corp.ext.listlabelgroups')
    def get_label_groups(self, size=20, offset=0):
        """
        获取系统标签
        :param size:
        :param offset:
        :return:
        """
        resp = get_label_groups(access_token=self.access_token, size=size, offset=offset)
        data = json.loads(resp['dingtalk_corp_ext_listlabelgroups_response']['result'])
        return data

    def get_all_label_groups(self):
        """
        获取全部的外部联系人标签
        :return:
        """
        size = 100
        offset = 0
        label_groups = []
        while True:
            # 钉钉接口存在Bug，偏移量已经超出数据数量时，仍会返回数据
            # 对此需要做特殊处理，今后如此Bug被修复，可以简化代码实现

            # 返回的数据是否重复
            valid_data = False
            # 获取钉钉的接口数据
            dd_label_groups = self.get_label_groups(size, offset)
            # 对数据进行循环，整理
            for dd_label_group in dd_label_groups:
                for label in dd_label_group['labels']:
                    label_group = {'color': dd_label_group['color'],
                                   'group': dd_label_group['name'],
                                   'name': label['name'],
                                   'id': label['id']}
                    if label_group not in label_groups:
                        label_groups.append(label_group)
                        valid_data = True
            # 当已经查询不到有效的新数据时，停止请求接口
            if valid_data is False:
                break
        return label_groups

    @dingtalk('dingtalk.corp.ext.list')
    def get_ext_list(self, size=20, offset=0):
        """
        获取外部联系人
        :return:
        """
        resp = get_corp_ext_list(self.access_token, size=size, offset=offset)
        result = json.loads(resp['dingtalk_corp_ext_list_response']['result'])
        return result

    def get_all_ext_list(self):
        """
        获取全部的外部联系人
        :return:
        """
        size = 100
        offset = 0
        dd_customer_list = []
        while True:
            dd_customers = self.get_ext_list(size=size, offset=offset)
            if len(dd_customers) <= 0:
                break
            else:
                dd_customer_list.extend(dd_customers)
                offset += size
        return dd_customer_list

    @dingtalk('dingtalk.corp.ext.add')
    def add_corp_ext(self, contact):
        """
        获取外部联系人
        :return:
        """
        resp = add_corp_ext(self.access_token, contact)
        return resp


if __name__ == '__main__':
    pass
