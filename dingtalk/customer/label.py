#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time: 2018/2/28 下午3:48
# @Author: BlackMatrix
# @Site: https://github.com/blackmatrix7
# @File: label
# @Software: PyCharm
from ..foundation import call_dingtalk_webapi, dingtalk_resp

__author__ = 'blackmatrix'

__all__ = ['get_label_groups']


@dingtalk_resp
def get_label_groups(access_token, size=20, offset=0):
    """
    获取标签列表
    :param access_token:
    :param size:
    :param offset:
    :return:
    """
    return call_dingtalk_webapi(access_token, 'dingtalk.corp.ext.listlabelgroups', 'GET', size=size, offset=offset)