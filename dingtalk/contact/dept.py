#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time: 2018/2/28 下午2:12
# @Author: BlackMatrix
# @Site: https://github.com/blackmatrix7
# @File: dept
# @Software: PyCharm
import requests
from ..configs import *
from ..foundation import dingtalk_resp

__author__ = 'blackmatrix'


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

if __name__ == '__main__':
    pass
