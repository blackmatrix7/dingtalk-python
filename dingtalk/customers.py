#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2017/11/30 下午2:50
# @Author : Matrix
# @Github : https://github.com/blackmatrix7/
# @Blog : http://www.cnblogs.com/blackmatrix/
# @File : customers.py
# @Software: PyCharm
import json
import requests
from .foundation import *

__author__ = 'blackmatrix'


@dingtalk_resp
def get_label_groups(access_token, size=20, offset=0):
    """
    获取标签列表
    :param access_token:
    :param size:
    :param offset:
    :return:
    """
    url = get_request_url(access_token, 'dingtalk.corp.ext.listlabelgroups')
    payload = {'size': size, 'offset': offset}
    return requests.get(url, params=payload)


@dingtalk_resp
def get_corp_ext_list(access_token, size=20, offset=0):
    """
    获取外部联系人
    :return:
    """
    url = get_request_url(access_token, 'dingtalk.corp.ext.list')
    payload = {'size': size, 'offset': offset}
    resp = requests.get(url, params=payload)
    return resp


@dingtalk_resp
def add_corp_ext(access_token, contact: dict):
    """
    新增外部联系人
    :return:
    """
    url = get_request_url(access_token, 'dingtalk.corp.ext.add')
    contact = json.dumps(contact)
    return requests.post(url, data={'contact': contact.encode('utf-8')})


if __name__ == '__main__':
    pass
