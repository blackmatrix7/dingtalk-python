#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time: 2018/2/28 下午3:12
# @Author: BlackMatrix
# @Site: https://github.com/blackmatrix7
# @File: ticket
# @Software: PyCharm
import hashlib
import requests
from dingtalk.configs import *
from dingtalk.foundation import dingtalk_resp

__author__ = 'blackmatrix'

__all__ = ['get_jsapi_ticket', 'generate_jsapi_signature']


@dingtalk_resp
def get_jsapi_ticket(accsess_token):
    params = {'access_token': accsess_token}
    data = requests.get(DING_GET_JSAPI_TICKET, params=params)
    return data


def generate_jsapi_signature(**kwargs):
    keys = sorted(kwargs)
    plain = ''
    for key in keys:
        plain += '{0}={1}&'.format(key, kwargs.get(key))
    plain = plain.strip('&')
    plain_bytes = plain.encode('utf-8')
    sha1 = hashlib.sha1(plain_bytes).hexdigest()
    return sha1

if __name__ == '__main__':
    pass
