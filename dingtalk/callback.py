#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2017/12/6 下午2:55
# @Author : Matrix
# @Github : https://github.com/blackmatrix7/
# @Blog : http://www.cnblogs.com/blackmatrix/
# @File : callback.py
# @Software: PyCharm
import base64
import requests
from .configs import *
from .foundation import dingtalk_resp

__author__ = 'blackmatrix'


@dingtalk_resp
def register_callback(access_token, token, callback_tag, aes_key, callback_url):
    """
    注册钉钉回调
    :param access_token:
    :param token:
    :param callback_tag:
    :param aes_key:
    :param callback_url:
    :return:
    """
    url = DING_REGISTER_CALL_BACK.format(access_token=access_token)
    payload = {'token': token, 'call_back_tag': callback_tag, 'aes_key': aes_key, 'url': callback_url}
    resp = requests.post(url, json=payload)
    return resp


@dingtalk_resp
def update_callback(access_token, token, callback_tag, aes_key, callback_url):
    """
    更新钉钉回调
    :param access_token:
    :param token:
    :param callback_tag:
    :param aes_key:
    :param callback_url:
    :return:
    """
    url = DING_UPDATE_CALL_BACK.format(access_token=access_token)
    payload = {'token': token, 'call_back_tag': callback_tag, 'aes_key': aes_key, 'url': callback_url}
    resp = requests.post(url, json=payload)
    return resp


@dingtalk_resp
def get_callback_failed_result(access_token):
    """
    获取回掉异常的数据
    :param access_token:
    :return:
    """
    url = DING_GET_CALL_BACK_FAILED_RESULT.format(access_token=access_token)
    resp = requests.get(url)
    return resp

if __name__ == '__main__':
    pass
