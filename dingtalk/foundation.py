#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2017/11/30 下午2:35
# @Author : Matrix
# @Github : https://github.com/blackmatrix7/
# @Blog : http://www.cnblogs.com/blackmatrix/
# @File : methods.py
# @Software: PyCharm
from datetime import datetime
from config import current_config

__author__ = 'blackmatrix'


def get_timestamp():
    """
    生成时间戳
    :return:
    """
    return datetime.now().strftime('yyyy-MM-dd HH:mm:ss')


def get_request_url(method, access_token, format_='json', v='2.0', simplify='false', partner_id=None):
    """
    通用的获取请求地址的方法
    :param method:
    :param access_token:
    :param format_:
    :param v:
    :param simplify:
    :param partner_id:
    :return:
    """
    timestamp = get_timestamp()
    url = '{0}?method={1}&session={2}&timestamp={3}&format={4}&v={5}'.format(
        current_config.DING_METHODS_URL, method, access_token, timestamp, format_, v)
    if format_ == 'json':
        url = '{0}&simplify={1}'.format(url, simplify)
    if partner_id:
        url = '{0}&partner_id={1}'.format(url, partner_id)
    return url




if __name__ == '__main__':
    pass
