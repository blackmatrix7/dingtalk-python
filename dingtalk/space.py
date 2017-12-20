#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2017/12/19 下午4:51
# @Author : Matrix
# @Github : https://github.com/blackmatrix7/
# @Blog : http://www.cnblogs.com/blackmatrix/
# @File : space.py
# @Software: PyCharm
import requests
from .configs import *
from .foundation import dingtalk_resp

__author__ = 'blackmatrix'


@dingtalk_resp
def get_custom_space(access_token, domain, agent_id):
    params = {'access_token': access_token, 'domain': domain, 'agent_id': agent_id}
    resp = requests.get(DING_GET_CSPACE, params=params)
    return resp


if __name__ == '__main__':
    pass
