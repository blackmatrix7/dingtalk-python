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
    # 获取外部联系人错误
    get_ext_list_err = SysException(err_code=3003, err_msg='获取外部联系人错误')
    # 获取标签错误
    get_labels_err = SysException(err_code=3004, err_msg='获取标签错误')
    # 获取部门错误
    get_departs_err = SysException(err_code=3005, err_msg='获取部门错误')
    # 获取用户错误
    get_users_err = SysException(err_code=3006, err_msg='获取用户错误')
    # 创建用户错误
    create_user_err = SysException(err_code=3007, err_msg='创建用户错误')
    # 更新用户错误
    update_user_err = SysException(err_code=3008, err_msg='更新用户错误')
    # 更新用户错误
    delete_user_err = SysException(err_code=3009, err_msg='删除用户错误')
    # 创建流程错误
    create_bmps_err = SysException(err_code=3009, err_msg='获取用户错误')


if __name__ == '__main__':
    pass
