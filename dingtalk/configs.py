#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2017/12/11 下午3:30
# @Author : Matrix
# @Github : https://github.com/blackmatrix7/
# @Blog : http://www.cnblogs.com/blackmatrix/
# @File : configs.py
# @Software: PyCharm

__author__ = 'blackmatrix'


DING_GET_ACCESS_TOKEN = 'https://oapi.dingtalk.com/gettoken'
DING_GET_JSAPI_TICKET = 'https://oapi.dingtalk.com/get_jsapi_ticket'
# 统一的方法URL
DING_METHODS_URL = 'https://eco.taobao.com/router/rest'
# 根据部门id获取用户列表
DING_GET_USER_LIST = 'https://oapi.dingtalk.com/user/simplelist'
# 获取用户
DING_GET_USER = 'https://oapi.dingtalk.com/user/get'
# 创建用户
DING_CREATE_USER = 'https://oapi.dingtalk.com/user/create?access_token={access_token}'
# 更新用户
DING_UPDATE_USER = 'https://oapi.dingtalk.com/user/update?access_token={access_token}'
# 删除用户
DING_DELETE_USER = 'https://oapi.dingtalk.com/user/delete?access_token={access_token}'
# 获取部门
DING_GET_DEPARTMENTS = 'https://oapi.dingtalk.com/department/list'


if __name__ == '__main__':
    pass
