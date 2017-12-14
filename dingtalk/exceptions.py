#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2017/11/28 下午3:29
# @Author : Matrix
# @Github : https://github.com/blackmatrix7/
# @Blog : http://www.cnblogs.com/blackmatrix/
# @File : exceptions.py
# @Software: PyCharm
from toolkit.exceptions import SysException

__author__ = 'blackmatrix'


class DingTalkExceptions:
    # 拒绝访问
    access_denied = SysException(err_code=3000, err_msg='访问拒绝')
    # 获取 access token 错误
    get_access_token_err = SysException(err_code=3001, err_msg='获取 access token 错误')
    # 获取 jsapi ticket 错误
    get_jsapi_ticket_err = SysException(err_code=3002, err_msg='获取 jsapi ticket 错误')
    # 钉钉接口返回错误
    dingtalk_resp_err = SysException(err_code=3003, err_msg='钉钉接口返回错误')
    # 钉钉接口参数不合法
    webapi_args_err = SysException(err_code=3003, err_msg='钉钉接口参数不合法')


if __name__ == '__main__':
    pass
