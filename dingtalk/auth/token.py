#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2017/11/28 上午11:47
# @Author : Matrix
# @Github : https://github.com/blackmatrix7/
# @Blog : http://www.cnblogs.com/blackmatrix/
# @File : token.py
# @Software: PyCharm
import requests
from ..apis import *
from ..foundation import dingtalk_resp

__author__ = 'blackmatrix'

__all__ = ['get_access_token']


@dingtalk_resp
def get_access_token(appkey, appsecret):
    """
    获取Access Token
    :return:
    """
    payload = {'appkey': appkey, 'appsecret': appsecret}
    return requests.get(DING_GET_ACCESS_TOKEN, params=payload)

if __name__ == '__main__':
    pass
