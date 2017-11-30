#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2017/11/30 下午3:57
# @Author : Matrix
# @Github : https://github.com/blackmatrix7/
# @Blog : http://www.cnblogs.com/blackmatrix/
# @File : department.py
# @Software: PyCharm
import requests
from .foundation import *
from config import current_config
from .exceptions import DingTalkExceptions

__author__ = 'blackmatrix'


def get_dempartment_list(access_token, id_=None, lang='zh_CN'):
    params = {'access_token': access_token, 'lang': lang}
    if id_:
        params.update({'id': id_})
    resp = requests.get(current_config.DING_GET_DEPARTMENTS, params=params)
    data = resp.json()
    if resp.status_code == 200 and data['errcode'] == 0:
        return data
    else:
        raise DingTalkExceptions.get_departs_err

if __name__ == '__main__':
    pass
