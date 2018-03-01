#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2017/11/28 上午9:22
# @Author : Matrix
# @Github : https://github.com/blackmatrix7/
# @Blog : http://www.cnblogs.com/blackmatrix/
# @File : __init__.py
# @Software: PyCharm

from .auth import Auth
from .file import File
from .contact import Contact
from .message import Message
from .customer import Customer
from .callback import CallBack
from .smartwork import SmartWork
from operator import methodcaller
from .exceptions import DingTalkExceptions

__author__ = 'blackmatrix'


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
                 noncestr='VCFGKFqgRA3xtYEhvVubdRY1DAvzKQD0AliCViy', domain='A2UOM1pZOxQ',
                 callback_url=None, aes_key='gbDjdBRfcxrwQA7nSFELj9c0HoWUpcfg8YURx7G84YI',
                 token='LnPxMAp7doy'):
        """
        实例化钉钉对象
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
        self.aes_key = aes_key
        self.token = token
        self.domain = domain
        self.noncestr = noncestr
        # 其他参数
        self.methods = {}
        # 钉钉接口模块
        # 鉴权模块需要先实例化，否则后续其他模块的实例化会出现异常
        self.auth = Auth(name=self.name, session_manager=session_manager, corp_id=corp_id, corp_secret=corp_secret)
        # 注册接口方法，为通过run方式调用提供支持
        self.register_methods(auth=self.auth)
        # 其他模块
        self.smartwork = SmartWork(self.access_token, self.agent_id)
        self.contact = Contact(self.access_token)
        self.message = Message(self.access_token, self.agent_id)
        self.file = File(self.access_token, self.domain, self.agent_id)
        self.customer = Customer(self.access_token)
        self.callback = CallBack(self.access_token, self.aes_key, self.token,
                                 self.callback_url, self.corp_id, self.noncestr)
        self.register_methods(smartwork=self.smartwork, contact=self.contact, message=self.message,
                              file=self.file, customer=self.customer)

    # ------------------- 基础方法 --------------------

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
        try:
            method_cfg = self.methods.get(method_name)
            module_name = method_cfg.get('module')
            func_name = method_cfg.get('func')
            module_ = getattr(self, module_name)
            f = methodcaller(func_name, *args, **kwargs)
            return f(module_)
        except AttributeError:
            raise AttributeError('没有找到对应的方法，可能是方法名有误，或dingtalk-python暂未实现此方法。')

    def register_methods(self, **modules):
        for module_name, module_obj in modules.items():
            for method_name, func_name in module_obj.methods.items():
                self.methods.update({method_name: {'module': module_name, 'func': func_name}})

    # ------------------- 鉴权部分允许通过子模块访问 --------------------

    def get_access_token(self):
        """
        在缓存中设置access token 7000秒过期，每次过期会自动重新获取 access token
        :return:
        """
        return self.auth.get_access_token()

    @property
    def access_token(self):
        return self.auth.get_access_token()

    def refresh_access_token(self, time_out=7000):
        """
        刷新access_token
        :return:
        """
        return self.auth.refresh_access_token(time_out=time_out)

    def get_jsapi_ticket(self):
        """
        获取当前缓存中的jsapi ticket
        如果没有命中缓存，则强制刷新jsticket
        :return:
        """
        return self.auth.get_jsapi_ticket()

    def refresh_jsapi_ticket(self, time_out=3600):
        """
        强制刷新 jsapi ticket
        :param time_out:
        :return:
        """
        return self.auth.refresh_jsapi_ticket(time_out=time_out)

    @property
    def jsapi_ticket(self):
        return self.get_jsapi_ticket()

    def jsapi_signature(self, jsapi_ticket, noncestr, timestamp, url):
        """
        计算签名信息
        :param jsapi_ticket:
        :param noncestr:
        :param timestamp:
        :param url:
        :return:
        """
        return self.auth.jsapi_signature(jsapi_ticket, noncestr, timestamp, url)

    # ------------------- 钉盘配置 --------------------

    @property
    def space_id(self):
        """
        获取space id
        https://open-doc.dingtalk.com/docs/doc.htm?spm=a219a.7629140.0.0.Fh7w2d&treeId=373&articleId=104970&docType=1#s2
        :return:
        """
        data = self.file.get_custom_space()
        return data['space_id']