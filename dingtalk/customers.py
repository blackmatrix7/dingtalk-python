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
from .exceptions import DingTalkExceptions

__author__ = 'blackmatrix'


def get_label_groups(access_token, size=20, offset=0):
    """
    获取标签列表
    :param access_token:
    :param size:
    :param offset:
    :return:
    """
    url = get_request_url('dingtalk.corp.ext.listlabelgroups', access_token)
    payload = {'size': size, 'offset': offset}
    resp = requests.get(url, params=payload)
    if resp.status_code == 200:
        return resp.json()
    else:
        raise DingTalkExceptions.get_ext_list_err


def get_corp_ext_list(access_token, size=20, offset=0):
    """
    获取外部联系人
    :return:
    """
    url = get_request_url('dingtalk.corp.ext.list', access_token)
    payload = {'size': size, 'offset': offset}
    resp = requests.get(url, params=payload)
    if resp.status_code == 200:
        return resp.json()
    else:
        raise DingTalkExceptions.get_ext_list_err


def add_corp_ext(access_token, contact: dict):
    """
    新增外部联系人
    :return:
    """
    url = get_request_url('dingtalk.corp.ext.add', access_token)
    contact = json.dumps(contact)
    resp = requests.post(url, data={'contact': contact.encode('utf-8')})
    if resp.status_code == 200:
        return resp.json()
    else:
        raise DingTalkExceptions.get_ext_list_err


if __name__ == '__main__':
    pass
