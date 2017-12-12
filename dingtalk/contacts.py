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
from .exceptions import DingTalkExceptions

__author__ = 'blackmatrix'


def get_user_list(access_token, department_id, lang='zh_CN', offset=0, size=20, order='entry_asc'):
    params = {'access_token': access_token, 'department_id': department_id, 'lang': lang, 'offset': offset,
              'size': size, 'order': order}
    resp = requests.get(DING_GET_USER_LIST, params=params)
    data = resp.json()
    if resp.status_code == 200 and data['errcode'] == 0:
        return data
    else:
        raise DingTalkExceptions.get_users_err


def get_user(access_token, userid):
    params = {'access_token': access_token, 'userid': userid}
    resp = requests.get(DING_GET_USER, params=params)
    data = resp.json()
    if resp.status_code == 200 and data['errcode'] == 0:
        return data
    else:
        raise DingTalkExceptions.get_users_err


def create_user(access_token, **user_info):
    """
    创建用户
    :param access_token:
    :param user_info:
    :return:
    """
    url = DING_CREATE_USER.format(access_token=access_token)
    resp = requests.post(url, json=user_info)
    data = resp.json()
    if resp.status_code == 200 and data['errcode'] == 0:
        return data
    else:
        raise DingTalkExceptions.create_user_err


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
    resp = requests.post(url, json=user_info)
    data = resp.json()
    if resp.status_code == 200 and data['errcode'] == 0:
        return data
    else:
        raise DingTalkExceptions.update_user_err


def delete_user(access_token, userid):
    url = DING_DELETE_USER.format(access_token=access_token)
    params = {'userid': userid}
    resp = requests.get(url, params=params)
    data = resp.json()
    if resp.status_code == 200 and data['errcode'] == 0:
        return data
    else:
        raise DingTalkExceptions.delete_user_err


def get_department_list(access_token, id_=None, lang='zh_CN'):
    params = {'access_token': access_token, 'lang': lang}
    if id_:
        params.update({'id': id_})
    resp = requests.get(DING_GET_DEPARTMENTS, params=params)
    data = resp.json()
    if resp.status_code == 200 and data['errcode'] == 0:
        return data
    else:
        raise DingTalkExceptions.get_departs_err


def get_department(access_token, id_):
    """
    获取部门详情
    :param access_token:
    :param id_:
    :return:
    """
    params = {'access_token': access_token, 'id': id_}
    resp = requests.get(DING_GET_DEPARTMENT, params=params)
    data = resp.json()
    if resp.status_code == 200 and data['errcode'] == 0:
        return data
    else:
        raise DingTalkExceptions.get_departs_err(data['errmsg'])


def create_department(access_token, **dept_info):
    url = DING_CREATE_DEPARTMENT.format(access_token=access_token)
    resp = requests.post(url, json=dept_info)
    data = resp.json()
    if resp.status_code == 200 and data['errcode'] == 0:
        return data
    else:
        raise DingTalkExceptions.create_depart_err(data['errmsg'])


def update_department(access_token, **dept_info):
    url = DING_UPDATE_DEPARTMENT.format(access_token=access_token)
    resp = requests.post(url, json=dept_info)
    data = resp.json()
    if resp.status_code == 200 and data['errcode'] == 0:
        return data
    else:
        raise DingTalkExceptions.create_depart_err


def delete_department(access_token, id_):
    params = {'access_token': access_token, 'id': id_}
    resp = requests.get(DING_DELETE_DEPARTMENT, params=params)
    data = resp.json()
    if resp.status_code == 200 and data['errcode'] == 0:
        return data
    else:
        raise DingTalkExceptions.delete_depart_err(data['errmsg'])



