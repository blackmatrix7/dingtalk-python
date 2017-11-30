#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2017/11/30 下午2:50
# @Author : Matrix
# @Github : https://github.com/blackmatrix7/
# @Blog : http://www.cnblogs.com/blackmatrix/
# @File : customers.py
# @Software: PyCharm
import requests
from .foundation import *
from .exceptions import DingTalkExceptions

__author__ = 'blackmatrix'


def get_corp_ext_list(access_token):
    """
    获取外部联系人
    :return:
    """
    url = get_request_url('dingtalk.corp.ext.list', access_token)
    resp = requests.get(url)
    if resp.status_code == 200:
        return resp.json()
    else:
        raise DingTalkExceptions.get_ext_list_err


def add_corp_ext():
    """
    新增外部联系人
    :return:
    """
    pass


if __name__ == '__main__':
    pass
