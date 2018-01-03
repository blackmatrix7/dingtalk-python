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
# 获取部门列表
DING_GET_DEPARTMENTS = 'https://oapi.dingtalk.com/department/list'
# 获取部门详情
DING_GET_DEPARTMENT = 'https://oapi.dingtalk.com/department/get'
# 创建部门
DING_CREATE_DEPARTMENT = 'https://oapi.dingtalk.com/department/create?access_token={access_token}'
# 更新部门
DING_UPDATE_DEPARTMENT = 'https://oapi.dingtalk.com/department/update?access_token={access_token}'
# 删除部门
DING_DELETE_DEPARTMENT = 'https://oapi.dingtalk.com/department/delete'
# 查询指定用户的所有上级父部门路径
DING_GET_USER_DEPARTMENTS = 'https://oapi.dingtalk.com/department/list_parent_depts'
# 获取企业员工人数
DING_GET_ORG_USER_COUNT = 'https://oapi.dingtalk.com/user/get_org_user_count'
# 通过CODE换取用户身份
DING_GET_USER_BY_CODE = 'https://oapi.dingtalk.com/user/getuserinfo'
# 获取企业下的自定义空间
DING_GET_CSPACE = 'https://oapi.dingtalk.com/cspace/get_custom_space'
# 注册回调
DING_REGISTER_CALL_BACK = 'https://oapi.dingtalk.com/call_back/register_call_back?access_token={access_token}'
# 获取回调失败结果
DING_GET_CALL_BACK_FAILED_RESULT = 'https://oapi.dingtalk.com/call_back/get_call_back_failed_result?access_token={access_token}'


if __name__ == '__main__':
    pass
