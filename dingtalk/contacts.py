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
from .foundation import dingtalk_resp, call_dingtalk_webapi

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


@dingtalk_resp
def get_user_departments(access_token, userid):
    params = {'access_token': access_token, 'userId': userid}
    return requests.get(DING_GET_USER_DEPARTMENTS, params=params)


@dingtalk_resp
def get_org_user_count(access_token, only_active):
    params = {'access_token': access_token, 'onlyActive': only_active}
    return requests.get(DING_GET_ORG_USER_COUNT, params=params)


@dingtalk_resp
def get_role_simple_list(access_token, role_id, size=20, offset=0):
    return call_dingtalk_webapi(access_token, 'dingtalk.corp.role.simplelist', 'POST',
                                role_id=role_id, size=size, offset=offset)


@dingtalk_resp
def get_corp_role_list(access_token, size=20, offset=0):
    return call_dingtalk_webapi(access_token, 'dingtalk.corp.role.list', 'GET',
                                size=size, offset=offset)


@dingtalk_resp
def add_roles_for_emps(access_token, rolelid_list: list, userid_list: list):
    """
    批量为一批用户添加一批角色信息。角色和员工是多对多的关系
    :param access_token:
    :param rolelid_list: 角色id list， 最大列表长度：20
    :param userid_list: 员工id list，最大列表长度：100
    :return:
    """
    if len(rolelid_list) > 20:
        raise DingTalkExceptions.webapi_args_err('角色id不能超过20个')
    if len(userid_list) > 100:
        raise DingTalkExceptions.webapi_args_err('员工id不能超过100个')
    return call_dingtalk_webapi(access_token, 'dingtalk.corp.role.addrolesforemps', 'POST',
                                rolelid_list=rolelid_list, userid_list=userid_list)


@dingtalk_resp
def remove_roles_for_emps(access_token, rolelid_list: list, userid_list: list):
    """
    企业在做企业员工管理的时候，需要对部分员工进行角色分类，该接口可以批量删除员工的角色信息。
    角色在钉钉的组织结构里面就是标签的意思，你可以批量为一批用户添加一批角色信息（dingtalk.corp.role.addrolesforemps），
    那么调用该接口就可以批量删除已经存在的角色和员工对应关系，角色和员工是多对多的关系。
    :param access_token:
    :param rolelid_list: 角色id list， 最大列表长度：20
    :param userid_list: 员工id list，最大列表长度：100
    :return:
    """
    if len(rolelid_list) > 20:
        raise DingTalkExceptions.webapi_args_err('角色id不能超过20个')
    if len(userid_list) > 100:
        raise DingTalkExceptions.webapi_args_err('员工id不能超过100个')
    return call_dingtalk_webapi(access_token, 'dingtalk.corp.role.removerolesforemps', 'POST',
                                rolelid_list=rolelid_list, userid_list=userid_list)


@dingtalk_resp
def get_role_group(access_token, group_id):
    """
    该接口通过groupId参数可以获取该角色组详细信息以及下面所有关联的角色的信息。
    :param access_token:
    :param group_id:
    :return:
    """
    return call_dingtalk_webapi(access_token, 'dingtalk.corp.role.removerolesforemps', 'GET', group_id=group_id)


