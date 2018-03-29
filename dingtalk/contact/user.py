#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2017/11/30 下午3:57
# @Author : Matrix
# @Github : https://github.com/blackmatrix7/
# @Blog : http://www.cnblogs.com/blackmatrix/
# @File : department.py
# @Software: PyCharm
import requests
from ..configs import *
from ..exceptions import DingTalkExceptions
from ..foundation import dingtalk_resp, call_dingtalk_webapi

__author__ = 'blackmatrix'

__all__ = ['get_user', 'update_user', 'create_user', 'delete_user', 'get_user_by_code',
           'get_dept_user_list', 'get_user_departments', 'get_org_user_count']


@dingtalk_resp
def get_dept_user_list(access_token, department_id, lang='zh_CN', offset=0, size=100, order='entry_asc'):
    params = {'access_token': access_token, 'department_id': department_id, 'lang': lang, 'offset': offset,
              'size': size, 'order': order}
    return requests.get(DING_GET_USER_LIST, params=params)


@dingtalk_resp
def get_user(access_token, userid):
    params = {'access_token': access_token, 'userid': userid}
    return requests.get(DING_GET_USER, params=params)


@dingtalk_resp
def create_user(access_token, **user_info):
    """
    创建用户
    :param access_token:
    :param user_info:
    :return:
    """
    url = DING_CREATE_USER.format(access_token=access_token)
    return requests.post(url, json=user_info)


@dingtalk_resp
def update_user(access_token, lang='zh_CN', **user_info):
    """
    更新用户
    :param access_token:
    :param lang:
    :param user_info:
    :return:
    """
    url = DING_UPDATE_USER.format(access_token=access_token)
    user_info.update({'lang': lang})
    return requests.post(url, json=user_info)


@dingtalk_resp
def delete_user(access_token, userid):
    url = DING_DELETE_USER.format(access_token=access_token)
    params = {'userid': userid}
    return requests.get(url, params=params)


@dingtalk_resp
def get_user_departments(access_token, userid):
    params = {'access_token': access_token, 'userId': userid}
    return requests.get(DING_GET_USER_DEPARTMENTS, params=params)


@dingtalk_resp
def get_org_user_count(access_token, only_active):
    params = {'access_token': access_token, 'onlyActive': only_active}
    return requests.get(DING_GET_ORG_USER_COUNT, params=params)


@dingtalk_resp
def get_user_by_code(access_token, code):
    params = {'access_token': access_token, 'code': code}
    resp = requests.get(DING_GET_USER_BY_CODE, params=params)
    return resp
