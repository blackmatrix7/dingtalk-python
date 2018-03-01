#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time: 2018/2/28 下午2:05
# @Author: BlackMatrix
# @Site: https://github.com/blackmatrix7
# @File: __init__.py
# @Software: PyCharm
from .user import *
from .dept import *
from .role import *
from functools import partial
from ..foundation import dingtalk_method

__author__ = 'blackmatrix'


METHODS = {}

method = partial(dingtalk_method, methods=METHODS)


class Contact:

    def __init__(self, access_token):
        self.access_token = access_token
        self.methods = METHODS

    # ------------------- 员工管理部分 -------------------

    def get_user(self, user_id):
        user_info = get_user(self.access_token, user_id)
        return user_info

    def get_user_list(self, department_id):
        """
        根据部门id获取用户列表
        :param department_id:
        :return:
        """
        data = get_user_list(self.access_token, department_id)
        user_list = data['userlist']
        return user_list

    def get_all_users(self):
        """
        获取整个组织架构下的所有员工
        根据部门Id遍历获取
        :return:
        """
        dept_list = self.get_department_list()
        for _dept in dept_list:
            del _dept['autoAddUser']
            del _dept['createDeptGroup']
            _dept['employees'] = self.get_user_list(_dept['id'])
        return dept_list

    def create_user(self, **user_info):
        """
        创建用户
        :param user_info:
        :return:
        """
        result = create_user(self.access_token, **user_info)
        return result

    def update_user(self, **user_info):
        """
        更新用户
        :param user_info:
        :return:
        """
        result = update_user(self.access_token, **user_info)
        return result

    def delete_user(self, userid):
        """
        删除用户
        :param userid:
        :return:
        """
        result = delete_user(self.access_token, userid)
        return result

    def get_org_user_count(self, only_active):
        """
        获取企业员工人数
        :param only_active: 0:非激活人员数量，1:已经激活人员数量
        :return:
        """
        data = get_org_user_count(self.access_token, only_active)
        return data['count']

    def get_user_departments(self, userid):
        """
        查询指定用户的所有上级父部门路径
        查询主管理员时，会返回无此用户，原因不明。
        可能是钉钉有意设置。
        :param userid:
        :return:
        """
        data = get_user_departments(self.access_token, userid)
        return data

    def get_user_by_code(self, code: str):
        """
        通过jsapi传入的code，向钉钉服务器换取用户信息
        :param code:
        :return:
        """
        data = get_user_by_code(self.access_token, code)
        return data

    # ------------------- 部门管理部分 -------------------

    def get_department_list(self, id_=None):
        """
        获取部门列表
        :param id_:
        :return:
        """
        data = get_department_list(self.access_token, id_)
        depart_list = data['department']
        return depart_list

    def get_department(self, id_):
        """
        根据部门Id获取部门
        :param id_:
        :return:
        """
        data = get_department(self.access_token, id_)
        return data

    def create_department(self, **dept_info):
        """
        创建部门
        :param dept_info:
        :return:
        """
        data = create_department(self.access_token, **dept_info)
        return data['id']

    def update_department(self, **dept_info):
        """
        更新部门信息
        :param dept_info:
        :return:
        """
        data = update_department(self.access_token, **dept_info)
        return data['id']

    def delete_department(self, id_):
        """
        根据部门id删除部门
        :param id_:
        :return:
        """
        data = delete_department(self.access_token, id_)
        return data

    # ------------------- 角色管理部分 -------------------

    @method('dingtalk.corp.role.list')
    def get_corp_role_list(self, size=20, offset=0):
        """
        获取企业角色列表（分页）
        https://open-doc.dingtalk.com/docs/doc.htm?spm=a219a.7629140.0.0.85WR2K&treeId=385&articleId=29205&docType=2
        :param size:
        :param offset:
        :return:
        """
        resp = get_corp_role_list(self.access_token, size=size, offset=offset)
        data = resp['dingtalk_corp_role_list_response']['result']['list']
        if data.get('role_groups') is None:
            return None
        else:
            role_groups = data.get('role_groups')
            for role_group in role_groups:
                # 钉钉返回的格式嵌套了两层roles，对格式做下处理
                role_group['roles'] = role_group.pop('roles').pop('roles')
            return role_groups

    @method('dingtalk.corp.role.all')
    def get_all_corp_role_list(self):
        """
        获取全部企业角色列表
        https://open-doc.dingtalk.com/docs/doc.htm?spm=a219a.7629140.0.0.85WR2K&treeId=385&articleId=29205&docType=2
        :return:
        """
        size = 100
        offset = 0
        dd_role_list = []
        while True:
            dd_roles = self.get_corp_role_list(size=size, offset=offset)
            if dd_roles is None or len(dd_roles) <= 0:
                break
            else:
                dd_role_list.extend(dd_roles)
                offset += size
        return dd_role_list

    @method('dingtalk.corp.role.simplelist')
    def get_role_simple_list(self, role_id, size=20, offset=0):
        """
        获取角色的员工列表
        https://open-doc.dingtalk.com/docs/doc.htm?spm=a219a.7629140.0.0.qatKNZ&treeId=385&articleId=29204&docType=2
        :param role_id:
        :param size:
        :param offset:
        :return:
        """
        data = get_role_simple_list(self.access_token, role_id=role_id, size=size, offset=offset)
        # 返回的数据格式，嵌套这么多层，不累吗？
        user_list = data['dingtalk_corp_role_simplelist_response']['result']['list']
        if user_list and 'emp_simple_list' in user_list:
            return user_list['emp_simple_list']

    @method('dingtalk.corp.role.getrolegroup')
    def get_role_group(self, group_id):
        """
        该接口通过group_id参数可以获取该角色组详细信息以及下面所有关联的角色的信息
        目前没有找到可以获取角色组id，即group_id的地方，如果获取角色组的话，可以使用dingtalk.corp.role.list获取
        但是只能获取到组名，没有角色组id，所以暂时不知道这个接口有什么用
        https://open-doc.dingtalk.com/docs/doc.htm?spm=a219a.7629140.0.0.VqsINY&treeId=385&articleId=29978&docType=2
        :param group_id:
        :return:
        """
        data = get_role_group(self.access_token, group_id=group_id)
        return data
