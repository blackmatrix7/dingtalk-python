#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2017/11/30 下午2:35
# @Author : Matrix
# @Github : https://github.com/blackmatrix7/
# @Blog : http://www.cnblogs.com/blackmatrix/
# @File : methods.py
# @Software: PyCharm
from .configs import *
from datetime import datetime
from .exceptions import DingTalkExceptions

__author__ = 'blackmatrix'


def get_timestamp():
    """
    生成时间戳
    :return:
    """
    return datetime.now().strftime('yyyy-MM-dd HH:mm:ss')


def get_request_url(access_token, method=None, format_='json', v='2.0', simplify='false', partner_id=None, url=None):
    """
    通用的获取请求地址的方法
    :param access_token:
    :param method:
    :param format_:
    :param v:
    :param simplify:
    :param partner_id:
    :param url:
    :return:
    """
    timestamp = get_timestamp()
    base_url = url or DING_METHODS_URL
    request_url = '{0}?method={1}&session={2}&timestamp={3}&format={4}&v={5}'.format(base_url, method, access_token,
                                                                                     timestamp, format_, v)
    if format_ == 'json':
        request_url = '{0}&simplify={1}'.format(request_url, simplify)
    if partner_id:
        request_url = '{0}&partner_id={1}'.format(request_url, partner_id)
    return request_url


def dingtalk_resp(func):
    def wrapper(*args, **kwargs):
        resp = func(*args, **kwargs)
        data = resp.json()
        if resp.status_code == 200:
            if 'errcode' in data and data['errcode'] != 0:
                raise DingTalkExceptions.dingtalk_resp_err(http_code=resp.status_code,
                                                           err_code=data['errcode'],
                                                           err_msg=data['errmsg'])
            elif 'error_response' in data and data['error_response']['code'] != 0:
                raise DingTalkExceptions.dingtalk_resp_err(http_code=resp.status_code,
                                                           err_code=data['error_response']['sub_code'],
                                                           err_msg=data['error_response']['sub_msg'])
            else:
                return data
        else:
            raise DingTalkExceptions.dingtalk_resp_err(http_code=resp.status_code,
                                                       err_code=data['errcode'],
                                                       err_msg=data['errmsg'])
    return wrapper
