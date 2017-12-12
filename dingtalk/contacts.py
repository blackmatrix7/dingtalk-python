#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2017/11/30 下午3:57
# @Author : Matrix
# @Github : https://github.com/blackmatrix7/
# @Blog : http://www.cnblogs.com/blackmatrix/
# @File : department.py
# @Software: PyCharm
import requests
from .configs import *
from .foundation import dingtalk_resp

__author__ = 'blackmatrix'


@dingtalk_resp
def get_user_list(access_token, department_id, lang='zh_CN', offset=0, size=20, order='entry_asc'):
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
def get_department_list(access_token, id_=None, lang='zh_CN'):
    params = {'access_token': access_token, 'lang': lang}
    if id_:
        params.update({'id': id_})
    return requests.get(DING_GET_DEPARTMENTS, params=params)


@dingtalk_resp
def get_department(access_token, id_):
    """
    获取部门详情
    :param access_token:
    :param id_:
    :return:
    """
    params = {'access_token': access_token, 'id': id_}
    return requests.get(DING_GET_DEPARTMENT, params=params)


@dingtalk_resp
def create_department(access_token, **dept_info):
    url = DING_CREATE_DEPARTMENT.format(access_token=access_token)
    return requests.post(url, json=dept_info)


@dingtalk_resp
def update_department(access_token, **dept_info):
    url = DING_UPDATE_DEPARTMENT.format(access_token=access_token)
    return requests.post(url, json=dept_info)


@dingtalk_resp
def delete_department(access_token, id_):
    params = {'access_token': access_token, 'id': id_}
    return requests.get(DING_DELETE_DEPARTMENT, params=params)


