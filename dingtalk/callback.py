#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2017/12/6 下午2:55
# @Author : Matrix
# @Github : https://github.com/blackmatrix7/
# @Blog : http://www.cnblogs.com/blackmatrix/
# @File : callback.py
# @Software: PyCharm
import requests
from .configs import *
from .foundation import dingtalk_resp

__author__ = 'blackmatrix'


@dingtalk_resp
def register_callback(access_token, callback_tag, aes_key, url):
    payload = {'token': access_token, 'callback_tag': callback_tag, 'aes_key': aes_key, 'url': aes_key}
    resp = requests.post(DING_REGISTER_CALL_BACK, json=payload)
    return resp

if __name__ == '__main__':
    pass
