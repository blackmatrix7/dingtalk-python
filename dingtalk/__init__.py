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
from time import sleep
from .contacts import *
from functools import wraps
from datetime import datetime
from operator import methodcaller
from .exceptions import DingTalkExceptions
from .foundation import get_timestamp, retry
from .workflow import create_bpms_instance, get_bpms_instance_list
from .customers import get_corp_ext_list, add_corp_ext, get_label_groups
from .auth import get_access_token, get_jsapi_ticket, generate_jsapi_signature
from .messages import async_send_msg, get_msg_send_result, get_msg_send_progress
from .callback import register_callback, get_callback_failed_result, update_callback

__author__ = 'blackmatrix'

METHODS = {}


def dingtalk(method_name):
    def wrapper(func):
        METHODS.update({method_name: func.__name__})

        @wraps(func)
        def _wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return _wrapper
    return wrapper


class SessionManager:
    """
    钉钉会话管理
    除了支持redis和memcached以外
    也可以通过实现此类的抽象方法支持mysql等数据库
    """

    def set(self, key, value, expires):
        """
        存储会话数据
        :param key:
        :param value:
        :param expires: 超时时间，单位秒
        :return:
        """
        raise NotImplementedError

    def get(self, key):
        """
        获取会话数据，获取时需要判断会话是否过期
        如已经会话数据已经过期，需要返回None
        :param key:
        :return:
        """
        raise NotImplementedError

    def delete(self, key):
        """
        删除会话数据
        :param key:
        :return:
        """
        raise NotImplementedError


class DingTalkApp:

    def __init__(self, name, session_manager, corp_id, corp_secret, agent_id=None,
                 noncestr=None, domain=None, callback_url=None, aes_key=None,
                 token=None):
        """

        :param name: 公司名称，同个公司如果需要实例化多个DingTalkApp实例，请保持传入的name值一致
        :param session_manager: 钉钉的会话管理对象
        :param corp_id: 钉钉的Corp Id，管理员可从后台获得
        :param corp_secret: 钉钉的Corp Secret，管理员可从后台获得
        :param agent_id: 钉钉的Agent Id，每个微应用有独立的agent_id，管理员可从后台获得
        :param noncestr: 随机字符串
        :param domain: 域名，可传入随机字符串
        :param callback_url: 回调函数地址，回调函数必须符合check_url方法的要求
        :param aes_key: 用于加解密的aes_key，必须是43为字符串，由大小写字母和数字组成，不能有标点符号
        :param token: 用于回调时生成签名的token，非access_token，传入随机字符串
        """
        self.name = name
        self.cache = session_manager
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
        return METHODS

    def get_access_token(self):
        """
        在缓存中设置access token 7000秒过期，每次过期会自动重新获取 access token
        :return:
        """
        access_token = None
        access_token_key = '{}_access_token'.format(self.name)
        try:
            if self.cache.get(access_token_key) is not None:
                access_token = self.cache.get(access_token_key)
                # 兼容redis
                try:
                    access_token = access_token.decode()
                except AttributeError:
                    pass
                logging.info('命中缓存{0}，直接返回缓存数据：{1}'.format(access_token_key, access_token))
            else:
                logging.warning('没有命中缓存{0}，准备重新向钉钉请求access token'.format(access_token_key))
                logging.info('先行清理缓存中的jsapi ticket数据')
                self.cache.delete('{}_jsapi_ticket'.format(self.name))
                time_out = 7000
                access_token = self.refresh_access_token(time_out)
        except BaseException as ex:
            logging.error('获取access token异常：{}'.format(ex))
        finally:
            return access_token

    def refresh_access_token(self, time_out=7000):
        """
        刷新access_token
        :return:
        """
        access_token_key = '{}_access_token'.format(self.name)
        self.cache.delete(access_token_key)
        logging.info('已清理access token相关缓存'.format(access_token_key))
        resp = get_access_token(self.corp_id, self.corp_secret)
        access_token = resp['access_token']
        logging.info('已重新向钉钉请求access token：{1}'.format(access_token_key, access_token))
        self.cache.set(access_token_key, access_token, time_out)
        logging.info('将{0}: {1} 写入缓存，过期时间{2}秒'.format(access_token_key, access_token, time_out))
        return access_token

    @property
    def access_token(self):
        return self.get_access_token()

    def get_jsapi_ticket(self):
        """
        获取当前缓存中的jsapi ticket
        如果没有命中缓存，则强制刷新jsticket
        :return:
        """
        jsapi_ticket_key = '{}_jsapi_ticket'.format(self.name)
        ticket_lock_key = '{}_ticket_lock'.format(self.name)

        def _get_jsapi_ticket():
            if self.cache.get(jsapi_ticket_key) is not None:
                ticket = self.cache.get(jsapi_ticket_key)
                # 兼容redis
                try:
                    ticket = ticket.decode()
                except AttributeError:
                    pass
                logging.info('命中缓存{}，直接返回缓存数据：{}'.format(jsapi_ticket_key, ticket))
            else:
                logging.warning('没有命中缓存{}，准备重新向钉钉请求 jsapi ticket'.format(jsapi_ticket_key))
                # jsapi ticket 过期时间，单位秒
                time_out = 3600
                # 获取jsapi ticket的锁
                ticket_lock = self.cache.get(ticket_lock_key)
                if ticket_lock and (ticket_lock is True or str(ticket_lock).lower() == 'true'):
                    logging.warning('jsapi ticket 存在锁，等待其他调用者请求新的 jsapi ticket')
                    sleep(0.5)
                    ticket = _get_jsapi_ticket()
                else:
                    logging.info('jsapi ticket 未加锁，可以请求新的 jsapi ticket')
                    ticket = self.refresh_jsapi_ticket(time_out)
            return ticket

        jsapi_ticket = _get_jsapi_ticket()
        return jsapi_ticket

    def refresh_jsapi_ticket(self, time_out=3600):
        """
        强制刷新 jsapi ticket
        :param time_out:
        :return:
        """
        jsapi_ticket_key = '{}_jsapi_ticket'.format(self.name)
        ticket_lock_key = '{}_ticket_lock'.format(self.name)
        ticket = None
        try:
            # 为jsapi ticket加锁
            self.cache.set(ticket_lock_key, True, 60)
            logging.info('已为jsapi ticket加锁，防止重复请求新的 jsapi ticket')
            # 主动清理之前的jsapi ticket缓存
            self.cache.delete(jsapi_ticket_key)
            # 检查是否清理成功
            assert self.cache.get(jsapi_ticket_key) is None
            # 请求新的jsapi ticket
            resp = get_jsapi_ticket(self.access_token)
            ticket = resp['ticket']
            logging.info('已向钉钉请求新的jsapi ticket：{}'.format(ticket))
            # 将新的jsapi ticket写入缓存
            self.cache.set(jsapi_ticket_key, ticket, time_out)
            logging.info('将jsapi ticket写入缓存{}：{}，过期时间{}秒'.format(jsapi_ticket_key, ticket, time_out))
        except Exception as ex:
            # 出现异常时，清理全部jsapi ticket的相关缓存数据
            self.cache.delete(jsapi_ticket_key)
            logging.error('强制刷新jsapi ticket出现异常，清理jsapi ticket缓存。异常信息：{}'.format(str(ex)))
        finally:
            # 解除jsticket的锁
            logging.info('解除jsapi ticket的锁{}，其他调用者可以请求新的jsapi ticket'.format(ticket_lock_key))
            self.cache.delete(ticket_lock_key)
            return ticket

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
        func_name = METHODS.get(method_name)
        if func_name is None:
            raise AttributeError('没有找到对应的方法，可能是方法名有误，或dingtalk-python暂未实现此方法。')
        f = methodcaller(func_name, *args, **kwargs)
        return f(self)

    def get_request_url(self, method, format_='json', v='2.0', simplify='false', partner_id=None):
        """
        获取请求url，会自动加入公共参数
        :param method:
        :param format_:
        :param v:
        :param simplify:
        :param partner_id:
        :return:
        """
        url = 'https://eco.taobao.com/router/rest?method={0}&session={1}&timestamp={2}&format={3}&v={4}'.format(
            method, self.access_token, self.timestamp, format_, v)
        if format_ == 'json':
            url = '{0}&simplify={1}'.format(url, simplify)
        if partner_id:
            url = '{0}&partner_id={1}'.format(url, partner_id)
        return url

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
        for dept in dept_list:
            del dept['autoAddUser']
            del dept['createDeptGroup']
            dept['employees'] = self.get_user_list(dept['id'])
        return dept_list

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
        """
        通过jsapi传入的code，向钉钉服务器换取用户信息
        :param code:
        :return:
        """
        data = get_user_by_code(self.access_token, code)
        return data

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
        # TODO 增加外部联系人时，钉钉一直返回"系统错误"四个字，原因不明
        resp = add_corp_ext(self.access_token, contact)
        return resp

    @dingtalk('dingtalk.smartwork.bpms.processinstance.create')
    def create_bpms_instance(self, process_code, originator_user_id, dept_id, approvers,
                             form_component_values, agent_id=None, cc_list=None, cc_position='FINISH'):
        """
        发起审批实例
        :param process_code:
        :param originator_user_id:
        :param dept_id:
        :param approvers:
        :param form_component_values:
        :param agent_id:
        :param cc_list:
        :param cc_position:
        :return:
        """
        agent_id = agent_id or self.agent_id
        data = create_bpms_instance(self.access_token, process_code, originator_user_id,
                                    dept_id, approvers, form_component_values,
                                    agent_id, cc_list, cc_position)
        return {'request_id': data['dingtalk_smartwork_bpms_processinstance_create_response']['request_id'],
                'success': data['dingtalk_smartwork_bpms_processinstance_create_response']['result']['is_success'],
                'process_instance_id': data['dingtalk_smartwork_bpms_processinstance_create_response']['result']['process_instance_id']}

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
        return {'request_id': data['dingtalk_smartwork_bpms_processinstance_list_response']['request_id'],
                'success': data['dingtalk_smartwork_bpms_processinstance_list_response']['result']['success'],
                'instance_list': instance_list,
                'next_cursor': next_cursor}

    def get_all_bpms_instance_list(self, process_code, start_time, end_time=None):
        """
        获取"全部"审批实例
        :param process_code:
        :param start_time: 起始时间，如果不传，默认当前时间往前推6个月
        :param end_time: 结束时间，如果不传，默认当前时间
        :return:
        """
        now = datetime.now()
        end_time = end_time or now
        if start_time > now or start_time > end_time:
            raise DingTalkExceptions.timestamp_err('起始时间不能晚于当前时间或结束时间')
        size = 10
        cursor = 0
        bpms_instance_list = []
        request_id = {}
        while True:
            result = self.get_bpms_instance_list(process_code, start_time, end_time=end_time, size=size, cursor=cursor)
            request_id.update({result['request_id']: {'success': result['success']}})
            bpms_instance_list.extend(result['instance_list'])
            if result['next_cursor'] > 0:
                cursor = result['next_cursor']
            else:
                break
        return {'request_id': request_id, 'bpms_instance_list': bpms_instance_list}

    @dingtalk('dingtalk.corp.message.corpconversation.asyncsend')
    def async_send_msg(self, msgtype, msgcontent, userid_list=None, dept_id_list=None, to_all_user=False):
        """
        异步发送消息
        接口文档：
        https://open-doc.dingtalk.com/docs/doc.htm?spm=a219a.7629140.0.0.C50a1Y&treeId=374&articleId=28915&docType=2
        消息内容格式说明：
        https://open-doc.dingtalk.com/docs/doc.htm?spm=a219a.7629140.0.0.CToLEy&treeId=374&articleId=104972&docType=1
        :param msgtype: 消息类型
        :param msgcontent: 消息内容
        :param userid_list: 发送的用户列表
        :param dept_id_list: 发送的部门列表
        :param to_all_user: 是否全员发送（全员发送有次数限制）
        :return:
        """
        resp = async_send_msg(access_token=self.access_token, agent_id=self.agent_id, msgtype=msgtype,
                              userid_list=userid_list, dept_id_list=dept_id_list, to_all_user=to_all_user,
                              msgcontent=msgcontent)
        return {'request_id': resp['dingtalk_corp_message_corpconversation_asyncsend_response']['request_id'],
                'task_id': resp['dingtalk_corp_message_corpconversation_asyncsend_response']['result']['task_id'],
                'success': resp['dingtalk_corp_message_corpconversation_asyncsend_response']['result']['success']}

    @dingtalk('dingtalk.corp.message.corpconversation.getsendresult')
    def get_msg_send_result(self, task_id, agent_id=None):
        """
        获取消息发送结果
        接口文档：
        https://open-doc.dingtalk.com/docs/doc.htm?spm=a219a.7629140.0.0.QvhuFr&treeId=374&articleId=28918&docType=2
        :param task_id: 发送消息时返回的task_id
        :param agent_id: 应用id
        :return:
        """
        agent_id = agent_id or self.agent_id
        resp = get_msg_send_result(self.access_token, agent_id, task_id)
        return {'request_id': resp['dingtalk_corp_message_corpconversation_getsendresult_response']['request_id'],
                'send_result': resp['dingtalk_corp_message_corpconversation_getsendresult_response']['result']['send_result'],
                'success': resp['dingtalk_corp_message_corpconversation_getsendresult_response']['result']['success']}

    @dingtalk('dingtalk.corp.message.corpconversation.getsendprogress')
    def get_msg_send_progress(self, task_id, agent_id=None):
        """
        获取企业发送消息进度
        接口文档：
        https://open-doc.dingtalk.com/docs/doc.htm?spm=a219a.7629140.0.0.68Lh70&treeId=374&articleId=28917&docType=2
        :param task_id: 发送消息时返回的task_id
        :param agent_id: 应用id
        :return:
        """
        agent_id = agent_id or self.agent_id
        resp = get_msg_send_progress(self.access_token, agent_id, task_id)
        return {'request_id': resp['dingtalk_corp_message_corpconversation_getsendprogress_response']['request_id'],
                'progress': resp['dingtalk_corp_message_corpconversation_getsendprogress_response']['result']['progress'],
                'success': resp['dingtalk_corp_message_corpconversation_getsendprogress_response']['result']['success']}

    @dingtalk('dingtalk.corp.role.list')
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

    @dingtalk('dingtalk.corp.role.all')
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

    @dingtalk('dingtalk.corp.role.simplelist')
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

    @dingtalk('dingtalk.corp.role.getrolegroup')
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

    def get_custom_space(self):
        data = get_custom_space(self.access_token, self.domain, self.agent_id)
        return {'space_id': data['spaceid'], 'success': True}

    @property
    def space_id(self):
        data = self.get_custom_space()
        return data['space_id']

    def register_callback(self, callback_tag):
        """
        向钉钉注册回调接口。
        注册回调前需要在初始化DingTalk App时传入aes_key和callback_url
        其中callback_url必须返回经过加密的字符串“success”的json数据
        可以使用return_success()方法直接返回一个符合要求的json格式。
        :param callback_tag:
        :return:
        """
        if self.aes_key is None or self.callback_url is None:
            raise RuntimeError('注册回调前需要在初始化DingTalk App时传入aes_key和callback_url')
        data = register_callback(self.access_token, self.token, callback_tag, self.aes_key, self.callback_url)
        return data

    def update_callback(self, callback_tag):
        if self.aes_key is None or self.callback_url is None:
            raise RuntimeError('更新回调前需要在初始化DingTalk App时传入aes_key和callback_url')
        data = update_callback(self.access_token, self.token, callback_tag, self.aes_key, self.callback_url)
        return data

    def encrypt(self, plaintext, buf=None):
        """
        钉钉加密数据
        :param plaintext: 明文
        :param buf:
        :return:
        """
        if self.aes_key is None:
            raise RuntimeError('加密解密前需要在初始化DingTalk App时传入aes_key')
        from .crypto import encrypt
        ciphertext = encrypt(aes_key=self.aes_key, plaintext=plaintext, key=self.corp_id, buf=buf)
        return ciphertext

    def encrypt_text(self, plaintext: str):
        """
        对纯文本进行加密
        :param plaintext: 明文
        :return:
        """
        if self.aes_key is None:
            raise RuntimeError('加密解密前需要在初始化DingTalk App时传入aes_key')
        from .crypto import encrypt_text
        ciphertext = encrypt_text(aes_key=self.aes_key, plaintext=plaintext)
        return ciphertext

    def decrypt(self, ciphertext: str):
        """
        钉钉解密数据
        :param ciphertext: 密文
        :return:
        """
        if self.aes_key is None:
            raise RuntimeError('加密解密前需要在初始化DingTalk App时传入aes_key')
        from .crypto import decrypt
        msg, key, buf = decrypt(self.aes_key, ciphertext)
        return msg, key, buf

    def decrypt_text(self, ciphertext: str):
        """
        对纯文本进行解密
        :param ciphertext: 密文
        :return:
        """
        if self.aes_key is None:
            raise RuntimeError('加密解密前需要在初始化DingTalk App时传入aes_key')
        from .crypto import decrypt_text
        temp = decrypt_text(self.aes_key, ciphertext)
        return temp

    def generate_callback_signature(self, data, timestamp, nonce):
        """
        创建回调函数的签名，可以用于验证钉钉回调时，传入的签名是否合法
        :param data:
        :param timestamp:
        :param nonce:
        :return:
        """
        from .crypto import generate_callback_signature
        sign = generate_callback_signature(self.token, data, timestamp, nonce)
        return sign

    def check_callback_signature(self, signature, ciphertext, timestamp, nonce):
        """
        验证钉钉回调接口的签名
        算法请访问
        https://open-doc.dingtalk.com/docs/doc.htm?spm=a219a.7386797.0.0.EkauZY&source=search&treeId=366&articleId=107524&docType=1
        :param signature: 需要验证的签名
        :param ciphertext: 加密后的数据
        :param timestamp: 时间戳
        :param nonce: 随机字符串
        :return:
        """
        from .crypto import check_callback_signature
        return check_callback_signature(self.token, ciphertext, signature, timestamp, nonce)

    def get_call_back_failed_result(self):
        """
        获取处理失败的钉钉回调
        :return:
        """
        data = get_callback_failed_result(self.access_token)
        return data['failed_list']

    def return_success(self):
        """
        钉钉回调需要返回含有success的json，提供一个方法，快速返回一个符合钉钉要求的success json
        :return:
        """
        # 加密success数据
        encrypt = self.encrypt('success').decode()
        # 创建时间戳
        timestamp = str(self.timestamp)
        # 获取随机字符串
        nonce = self.noncestr
        # 创建签名
        signature = self.generate_callback_signature(encrypt, timestamp, nonce)
        # 返回结果
        return {'msg_signature': signature, 'timeStamp': timestamp, 'nonce': nonce, 'encrypt': encrypt}

    def check_url(self, ding_nonce, ding_sign, ding_timestamp, ding_encrypt):
        """
        一个钉钉注册回调的check_url方法
        文档：
        https://open-doc.dingtalk.com/docs/doc.htm?spm=a219a.7629140.0.0.x75fVY&treeId=385&articleId=104975&docType=1#s12
        :param ding_nonce: 钉钉返回的随机字符串
        :param ding_sign: 钉钉返回的签名
        :param ding_timestamp: 钉钉返回的时间戳
        :param ding_encrypt: 钉钉返回的加密后数据
        :return: 返回带success的json
        """
        # 验证签名
        if self.check_callback_signature(ding_sign, ding_encrypt, ding_timestamp, ding_nonce) is False:
            raise DingTalkExceptions.sign_err
        # 签名验证成功后，解密数据
        ding_data, corp_id, buf = self.decrypt(ding_encrypt)
        assert ding_data and corp_id and buf
        # 返回结果
        result = self.return_success()
        return result

if __name__ == '__main__':
    pass
