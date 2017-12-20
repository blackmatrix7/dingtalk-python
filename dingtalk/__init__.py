#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2017/11/28 上午9:22
# @Author : Matrix
# @Github : https://github.com/blackmatrix7/
# @Blog : http://www.cnblogs.com/blackmatrix/
# @File : __init__.py.py
# @Software: PyCharm
import json
import logging
from .space import *
from .contacts import *
from toolkit.retry import retry
from json import JSONDecodeError
from operator import methodcaller
from .foundation import get_timestamp
from .workflow import create_bpms_instance, get_bpms_instance_list
from .auth import get_access_token, get_jsapi_ticket, create_signature
from .customers import get_corp_ext_list, add_corp_ext, get_label_groups
from .messages import async_send_msg, get_msg_send_result, get_msg_send_progress

__author__ = 'blackmatrix'

no_value = object()

methods = {}


def dingtalk(method_name):
    def wrapper(func):
        methods.update({method_name: func.__name__})

        def _wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return _wrapper
    return wrapper


class DingTalkApp:

    def __init__(self, name, cache, corp_id, corp_secret, agent_id=None, noncestr=None, domain=None):
        self.name = name
        self.cache = cache
        self.corp_id = corp_id
        self.corp_secret = corp_secret
        self.agent_id = agent_id
        self.domain = domain or 'A2UOM1pZOxQ'
        self.noncestr = noncestr or 'VCFGKFqgRA3xtYEhvVubdRY1DAvzKQD0AliCViy'

    @property
    def methods(self):
        return methods

    def get_access_token(self):
        """
        在缓存中设置access token 7000秒过期，每次过期会自动重新获取 access token
        :return:
        """
        key_name = '{}_access_token'.format(self.name)

        @self.cache.cached(key_name, 7000)
        def _get_access_token():
            resp = get_access_token(self.corp_id, self.corp_secret)
            data = resp['access_token']
            return data
        access_token = _get_access_token()
        return access_token

    def refresh_access_token(self):
        """
        刷新access_token
        :return:
        """
        key_name = '{}_access_token'.format(self.name)
        resp = get_access_token(self.corp_id, self.corp_secret)
        access_token = resp['access_token']
        self.cache.set(key_name, access_token, 7000)
        return access_token

    @property
    def access_token(self):
        return self.get_access_token()

    def get_jsapi_ticket(self):
        jsapi_ticket_key = '{}_jsapi_ticket'.format(self.name)
        access_token_key = '{}_access_token'.format(self.name)

        @self.cache.delcache(access_token_key)
        @self.cache.delcache(jsapi_ticket_key)
        def callback(err):
            logging.error(err)

        @retry(max_retries=5, step=5, callback=callback)
        @self.cache.cached(jsapi_ticket_key, 3000)
        def _get_jsapi_ticket():
            resp = get_jsapi_ticket(self.access_token)
            ticket = resp['ticket']
            return ticket
        jsapi_ticket = _get_jsapi_ticket()
        return jsapi_ticket

    @property
    def jsapi_ticket(self):
        return self.get_jsapi_ticket()

    @staticmethod
    def signature(jsapi_ticket, noncestr, timestamp, url):
        """
        计算签名信息
        :param jsapi_ticket:
        :param noncestr:
        :param timestamp:
        :param url:
        :return:
        """
        logging.info('jsapi_ticket:{}'.format(jsapi_ticket))
        logging.info('noncestr:{}'.format(noncestr))
        logging.info('timestamp:{}'.format(timestamp))
        logging.info('url:{}'.format(url))
        sign = create_signature(jsapi_ticket=jsapi_ticket, noncestr=noncestr, timestamp=timestamp, url=url)
        logging.info('sign:{}'.format(sign))
        return sign

    @property
    def timestamp(self):
        return get_timestamp()

    def run(self, method_name, *args, **kwargs):
        """
        传入方法名和参数，直接调用指定的钉钉接口，参数只需要传入钉钉的请求参数部分；
        不需要传入钉钉的公共参数部分，公共参数会自动补完。
        例如，需要调用"获取外部联系人标签"的接口，伪代码：
        app = DingTalkApp(.....)
        app.run('dingtalk.corp.ext.listlabelgroups', size=20, offset=0)
        :param method_name:
        :param args:
        :param kwargs:
        :return:
        """
        func_name = methods.get(method_name)
        if func_name is None:
            raise AttributeError('没有找到对应的方法，可能是方法名有误，或SDK暂未实现此方法。')
        f = methodcaller(func_name, *args, **kwargs)
        return f(self)

    def get_request_url(self, method, format_='json', v='2.0', simplify='false', partner_id=None):
        url = 'https://eco.taobao.com/router/rest?method={0}&session={1}&timestamp={2}&format={3}&v={4}'.format(
            method, self.access_token, self.timestamp, format_, v)
        if format_ == 'json':
            url = '{0}&simplify={1}'.format(url, simplify)
        if partner_id:
            url = '{0}&partner_id={1}'.format(url, partner_id)
        return url

    def get_user_list(self, department_id=None):
        data = get_user_list(self.access_token, department_id)
        user_list = data['userlist']
        return user_list

    def get_user_info(self, user_id):
        user_info = get_user(self.access_token, user_id)
        return user_info

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

    def get_user_by_code(self, code: str):
        data = get_user_by_code(self.access_token, code)
        return data

    def get_department_list(self, id_=None):
        data = get_department_list(self.access_token, id_)
        depart_list = data['department']
        return depart_list

    def get_department(self, id_):
        data = get_department(self.access_token, id_)
        return data

    def create_department(self, **dept_info):
        data = create_department(self.access_token, **dept_info)
        return data['id']

    def update_department(self, **dept_info):
        data = update_department(self.access_token, **dept_info)
        return data['id']

    def delete_department(self, id_):
        data = delete_department(self.access_token, id_)
        return data

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

    def get_org_user_count(self, only_active):
        """
        获取企业员工人数
        :param only_active: 0:非激活人员数量，1:已经激活人员数量
        :return:
        """
        data = get_org_user_count(self.access_token, only_active)
        return data['count']

    @dingtalk('dingtalk.corp.ext.listlabelgroups')
    def get_label_groups(self, size=20, offset=0):
        """
        获取系统标签
        :param size:
        :param offset:
        :return:
        """
        resp = get_label_groups(access_token=self.access_token, size=size, offset=offset)
        data = json.loads(resp['dingtalk_corp_ext_listlabelgroups_response']['result'])
        return data

    def get_all_label_groups(self):
        """
        获取全部的外部联系人标签
        :return:
        """
        size = 100
        offset = 0
        label_groups = []
        while True:
            # 钉钉接口存在Bug，偏移量已经超出数据数量时，仍会返回数据
            # 对此需要做特殊处理，今后如此Bug被修复，可以简化代码实现

            # 返回的数据是否重复
            valid_data = False
            # 获取钉钉的接口数据
            dd_label_groups = self.get_label_groups(size, offset)
            # 对数据进行循环，整理
            for dd_label_group in dd_label_groups:
                for label in dd_label_group['labels']:
                    label_group = {'color': dd_label_group['color'],
                                   'group': dd_label_group['name'],
                                   'name': label['name'],
                                   'id': label['id']}
                    if label_group not in label_groups:
                        label_groups.append(label_group)
                        valid_data = True
            # 当已经查询不到有效的新数据时，停止请求接口
            if valid_data is False:
                break
        return label_groups

    @dingtalk('dingtalk.corp.ext.list')
    def get_ext_list(self, size=20, offset=0):
        """
        获取外部联系人
        :return:
        """
        resp = get_corp_ext_list(self.access_token, size=size, offset=offset)
        result = json.loads(resp['dingtalk_corp_ext_list_response']['result'])
        return result

    def get_all_ext_list(self):
        """
        获取全部的外部联系人
        :return:
        """
        size = 100
        offset = 0
        dd_customer_list = []
        while True:
            dd_customers = self.get_ext_list(size=size, offset=offset)
            if len(dd_customers) <= 0:
                break
            else:
                dd_customer_list.extend(dd_customers)
                offset += size
        return dd_customer_list

    @dingtalk('dingtalk.corp.ext.add')
    def add_corp_ext(self, contact):
        """
        获取外部联系人
        :return:
        """
        resp = add_corp_ext(self.access_token, contact)
        return resp

    @dingtalk('dingtalk.smartwork.bpms.processinstance.create')
    def create_bpms_instance(self, process_code, originator_user_id, dept_id, approvers, form_component_values, agent_id=None):
        """
        发起审批实例
        :param process_code:
        :param originator_user_id:
        :param dept_id:
        :param approvers:
        :param form_component_values:
        :param agent_id:
        :return:
        """
        agent_id = agent_id or self.agent_id
        try:
            form_component_values = json.dumps(form_component_values)
        except JSONDecodeError:
            pass
        resp = create_bpms_instance(self.access_token, process_code, originator_user_id,
                                    dept_id, approvers, form_component_values, agent_id)
        return resp

    @dingtalk('dingtalk.smartwork.bpms.processinstance.list')
    def get_bpms_instance_list(self, process_code, start_time, end_time=None, size=10, cursor=0):
        resp = get_bpms_instance_list(self.access_token, process_code, start_time, end_time, size, cursor)
        return resp

    @dingtalk('dingtalk.corp.message.corpconversation.asyncsend')
    def async_send_msg(self, msgtype, msgcontent, userid_list=None, dept_id_list=None, to_all_user=False):
        resp = async_send_msg(access_token=self.access_token, agent_id=self.agent_id, msgtype=msgtype,
                              userid_list=userid_list, dept_id_list=dept_id_list, to_all_user=to_all_user,
                              msgcontent=msgcontent)
        return resp

    @dingtalk('dingtalk.corp.message.corpconversation.getsendresult')
    def get_msg_send_result(self, task_id, agent_id=None):
        agent_id = agent_id or self.agent_id
        resp = get_msg_send_result(self.access_token, agent_id, task_id)
        return resp

    @dingtalk('dingtalk.corp.message.corpconversation.getsendprogress')
    def get_msg_send_progress(self, task_id, agent_id=None):
        agent_id = agent_id or self.agent_id
        resp = get_msg_send_progress(self.access_token, agent_id, task_id)
        return resp

    @dingtalk('dingtalk.corp.role.list')
    def get_corp_role_list(self, size=20, offset=0):
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

    def get_all_corp_role_list(self):
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

    @dingtalk('dingtalk.corp.role.simplelist')
    def get_role_simple_list(self, role_id, size=20, offset=0):
        data = get_role_simple_list(self.access_token, role_id=role_id, size=size, offset=offset)
        # 返回的数据格式，嵌套这么多层，不累吗？
        user_list = data['dingtalk_corp_role_simplelist_response']['result']['list']
        if user_list and 'emp_simple_list' in user_list:
            return user_list['emp_simple_list']

    @dingtalk('dingtalk.corp.role.getrolegroup')
    def get_role_group(self, group_id):
        data = get_role_group(self.access_token, group_id=group_id)
        return data

    def get_customer_space(self):
        data = get_custom_space(self.access_token, self.domain, self.agent_id)
        return data['spaceid']

    @property
    def space_id(self):
        return self.get_customer_space()

if __name__ == '__main__':
    pass
