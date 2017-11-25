#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2017/11/28 上午11:47
# @Author : Matrix
# @Github : https://github.com/blackmatrix7/
# @Blog : http://www.cnblogs.com/blackmatrix/
# @File : token.py
# @Software: PyCharm
import requests
from config import current_config
from .exceptions import DingTalkExceptions

__author__ = 'blackmatrix'


def get_access_token(corp_id, corp_secret):
    """
    获取Access Token
    :return:
    """
    payload = {'corpid': corp_id, 'corpsecret': corp_secret}
    resp = requests.get(current_config.DING_GET_ACCESS_TOKEN, params=payload)
    if resp.status_code == 200:
        data = resp.json()
        if data['errcode'] == 0 and data['errmsg'] == 'ok':
            return data
        else:
            raise DingTalkExceptions.get_access_token_err
    else:
        raise DingTalkExceptions.get_access_token_err


def get_jsapi_ticket(accsess_token):
    payload = {'access_token': accsess_token}
    resp = requests.get(current_config.DING_GET_JSAPI_TICKET, params=payload)
    if resp.status_code == 200:
        data = resp.json()
        if data['errcode'] == 0 and data['errmsg'] == 'ok':
            return data
        else:
            raise DingTalkExceptions.get_jsapi_ticket_err
    else:
        raise DingTalkExceptions.get_jsapi_ticket_err


def sign(ticket, nonce_str, time_stamp, url):
    import hashlib
    plain = 'jsapi_ticket={0}&&noncestr={1}&&timestamp={2}&url={3}'.format(ticket, nonce_str, time_stamp, url)
    plain_bytes = plain.encode('utf-8')
    sha1 = hashlib.sha1(plain_bytes).hexdigest()
    return sha1

if __name__ == '__main__':
    pass
