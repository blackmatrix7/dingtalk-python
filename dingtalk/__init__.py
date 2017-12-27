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
from .callback import *
from datetime import datetime
from toolkit.retry import retry
from json import JSONDecodeError
from operator import methodcaller
from .foundation import get_timestamp
from dateutil.relativedelta import relativedelta
from .workflow import create_bpms_instance, get_bpms_instance_list
from .customers import get_corp_ext_list, add_corp_ext, get_label_groups
from .auth import get_access_token, get_jsapi_ticket, generate_jsapi_signature
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

    def __init__(self, name, cache, corp_id, corp_secret, agent_id=None,
                 noncestr=None, domain=None, callback_url=None, aes_key=None,
                 token=''):
        self.name = name
        self.cache = cache
        self.corp_id = corp_id
        self.corp_secret = corp_secret
        self.agent_id = agent_id
        self.callback_url = callback_url
        # AES_KEY
        self.aes_key = aes_key or 'gbDjdBRfcxrwQA7nSFELj9c0HoWUpcfg8YURx7G84YI'
        self.token = token or 'LnPxMAp7doy'
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
        if self.cache.get(key_name) is not None:
            data = self.cache.get(key_name)
        else:
            resp = get_access_token(self.corp_id, self.corp_secret)
            data = resp['access_token']
            self.cache.set(key_name, data, 7000)
        return data

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

        def _callback(err):
            logging.error(err)
            try:
                self.cache.delete(access_token_key)
                self.cache.delete(jsapi_ticket_key)
            except Exception as ex:
                logging.error(ex)

        @retry(max_retries=5, step=5, callback=_callback)
        def _get_jsapi_ticket():
            if self.cache.get(jsapi_ticket_key):
                ticket = self.cache.get(jsapi_ticket_key)
            else:
                resp = get_jsapi_ticket(self.access_token)
                ticket = resp['ticket']
                self.cache.set(jsapi_ticket_key, ticket, 3000)
            return ticket

        jsapi_ticket = _get_jsapi_ticket()
        return jsapi_ticket

    @property
    def jsapi_ticket(self):
        return self.get_jsapi_ticket()

    @staticmethod
    def jsapi_signature(jsapi_ticket, noncestr, timestamp, url):
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
        sign = generate_jsapi_signature(jsapi_ticket=jsapi_ticket, noncestr=noncestr, timestamp=timestamp, url=url)
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
        # 实例化一个DingTalk App
        app = DingTalkApp(.....)
        # 传入需要调用的接口方法名及参数，返回接口调用结果
        data = app.run('dingtalk.corp.ext.listlabelgroups', size=20, offset=0)
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
        """

        :param process_code:
        :param start_time:
        :param end_time:
        :param size: 每次获取的记录条数，最大只能是10
        :param cursor:
        :return:
        """
        data = get_bpms_instance_list(self.access_token, process_code, start_time, end_time, size, cursor)
        instance_list = data['dingtalk_smartwork_bpms_processinstance_list_response']['result']['result']['list'].get('process_instance_top_vo', [])
        next_cursor = data['dingtalk_smartwork_bpms_processinstance_list_response']['result']['result'].get('next_cursor', 0)
        return instance_list, next_cursor

    def get_all_bpms_instance_list(self, process_code, start_time=None, end_time=None):
        """

        :param process_code:
        :param start_time: 起始时间，如果不传，默认当前时间往前推6个月
        :return:
        """
        now = datetime.now()
        start_time = start_time or now - relativedelta(month=6)
        end_time = end_time or now
        size = 10
        cursor = 0
        bpms_instance_list = []
        while True:
            instance_list, next_cursor = self.get_bpms_instance_list(process_code, start_time, end_time=end_time, size=size, cursor=cursor)
            bpms_instance_list.extend(instance_list)
            if next_cursor > 0:
                cursor = next_cursor
            else:
                break
        return bpms_instance_list

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
        return data

    @property
    def space_id(self):
        data = self.get_customer_space()
        return data['spaceid']

    def register_callback(self, callback_tag):
        """
        向钉钉注册回调接口。
        注册回调前需要在初始化DingTalk App时传入aes_key和callback_url
        其中callback_url必须返回经过加密的字符串“success”的json数据
        :param callback_tag:
        :return:
        """
        if self.aes_key is None or self.callback_url is None:
            raise RuntimeError('注册回调前需要在初始化DingTalk App时传入aes_key和callback_url')
        data = register_callback(self.access_token, self.token, callback_tag, self.aes_key, self.callback_url)
        return data

    def encrypt(self, plaintext, buf=None):
        """
        钉钉加密数据
        :param plaintext:
        :param buf:
        :return:
        """
        if self.aes_key is None:
            raise RuntimeError('加密解密前需要在初始化DingTalk App时传入aes_key')
        from .crypto import encrypt
        ciphertext = encrypt(aes_key=self.aes_key, plaintext=plaintext, key=self.corp_id, buf=buf)
        return ciphertext

    def encrypt_str(self, plaintext):
        """
        钉钉加密数据
        :param plaintext:
        :return:
        """
        if self.aes_key is None:
            raise RuntimeError('加密解密前需要在初始化DingTalk App时传入aes_key')
        from .crypto import encrypt_str
        ciphertext = encrypt_str(aes_key=self.aes_key, plaintext=plaintext)
        return ciphertext

    def decrypt(self, ciphertext):
        """
        钉钉解密数据
        :param ciphertext:
        :return:
        """
        if self.aes_key is None:
            raise RuntimeError('加密解密前需要在初始化DingTalk App时传入aes_key')
        from .crypto import decrypt
        msg, key, buf = decrypt(self.aes_key, ciphertext)
        return msg, key, buf

    def decrypt_str(self, ciphertext):
        """
        钉钉解密数据
        :param ciphertext:
        :return:
        """
        if self.aes_key is None:
            raise RuntimeError('加密解密前需要在初始化DingTalk App时传入aes_key')
        from .crypto import decrypt_str
        temp = decrypt_str(self.aes_key, ciphertext)
        return temp

    def generate_signature(self, data, timestamp, nonce):
        from .crypto import generate_signature
        sign = generate_signature(self.access_token, data, timestamp, nonce)
        return sign

    def check_signature(self, signature, data, timestamp, nonce):
        from .crypto import check_signature
        return check_signature(self.access_token, data, signature, timestamp, nonce)

if __name__ == '__main__':
    pass
