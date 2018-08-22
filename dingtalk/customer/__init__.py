#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time: 2018/2/28 下午3:46
# @Author: BlackMatrix
# @Site: https://github.com/blackmatrix7
# @File: __init__.py
# @Software: PyCharm
import json
import logging
from .ext import *
from .label import *
from functools import partial
from ..foundation import dingtalk_method

__author__ = 'blackmatrix'

METHODS = {}

method = partial(dingtalk_method, methods=METHODS)


class Customer:

    def __init__(self, auth, logger=logging):
        self.auth = auth
        self.methods = METHODS
        self.logger = logger

    @method(method_name='dingtalk.corp.ext.listlabelgroups')
    def get_label_groups(self, size=20, offset=0):
        """
        获取系统标签
        :param size:
        :param offset:
        :return:
        """
        resp = get_label_groups(access_token=self.auth.access_token, size=size, offset=offset)
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
                for dd_label in dd_label_group['labels']:
                    label_group = {'color': dd_label_group['color'],
                                   'group': dd_label_group['name'],
                                   'name': dd_label['name'],
                                   'id': dd_label['id']}
                    if label_group not in label_groups:
                        label_groups.append(label_group)
                        valid_data = True
            # 当已经查询不到有效的新数据时，停止请求接口
            if valid_data is False:
                break
        return label_groups

    @method('dingtalk.corp.ext.list')
    def get_ext_list(self, size=20, offset=0):
        """
        获取外部联系人
        :return:
        """
        resp = get_corp_ext_list(self.auth.access_token, size=size, offset=offset)
        result = json.loads(resp['dingtalk_corp_ext_list_response']['result'])
        return result

    @method('dingtalk.corp.ext.all')
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
        添加外部联系人
        如果遇到添加外部联系人失败的情况，请检查在钉钉设置中，外部联系人是否存在某些必填自定义字段
        存在必填自定义字段的情况下，通过接口添加外部联系人会失败，而且钉钉只会返回"系统错误"四个字
        :return:
        """
        resp = add_corp_ext(self.auth.access_token, contact_info)
        return resp
