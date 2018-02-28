#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time: 2018/2/28 下午3:46
# @Author: BlackMatrix
# @Site: https://github.com/blackmatrix7
# @File: __init__.py
# @Software: PyCharm
import json
from .ext import *
from .label import *

__author__ = 'blackmatrix'


class Customer:

    def __init__(self, access_token):
        self.access_token = access_token

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

    def add_corp_ext(self, contact_info):
        """
        获取外部联系人
        :return:
        """
        # TODO 增加外部联系人时，钉钉一直返回"系统错误"四个字，原因不明
        resp = add_corp_ext(self.access_token, contact_info)
        return resp

if __name__ == '__main__':
    pass
