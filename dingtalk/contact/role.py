#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time: 2018/2/28 下午2:30
# @Author: BlackMatrix
# @Site: https://github.com/blackmatrix7
# @File: role
# @Software: PyCharm
from ..exceptions import DingTalkExceptions
from ..foundation import dingtalk_resp, call_dingtalk_webapi

__author__ = 'blackmatrix'

__all__ = ['get_role_simple_list', 'get_corp_role_list', 'add_roles_for_emps', 'remove_roles_for_emps', 'get_role_group']


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
