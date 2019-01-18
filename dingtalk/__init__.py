#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2017/11/28 上午9:22
# @Author : Matrix
# @Github : https://github.com/blackmatrix7/
# @Blog : http://www.cnblogs.com/blackmatrix/
# @File : __init__.py
# @Software: PyCharm
import logging
from .auth import Auth
from .file import File
from .contact import Contact
from .message import Message
from .customer import Customer
from .smartwork import SmartWork
from operator import methodcaller
from .foundation import get_timestamp
from .exceptions import DingTalkExceptions

__author__ = 'blackmatrix'


class DingTalkApp:

    def __init__(self, name, session_manager, corp_id, corp_secret,
                 appkey, appsecret, agent_id=None,
                 noncestr='VCFGKFqgRA3xtYEhvVubdRY1DAvzKQD0AliCViy', domain='A2UOM1pZOxQ',
                 callback_url=None, aes_key='gbDjdBRfcxrwQA7nSFELj9c0HoWUpcfg8YURx7G84YI',
                 token='LnPxMAp7doy', logger=logging):
        """
        实例化钉钉对象
        :param name: 公司名称，同个公司如果需要实例化多个DingTalkApp实例，请保持传入的name值一致
        :param session_manager: 钉钉的会话管理对象
        :param corp_id: 钉钉的Corp Id，管理员可从后台获得
        :param corp_secret: 钉钉的Corp Secret，管理员可从后台获得
        :param appkey: 钉钉应用的 key，创建应用后获得
        :param appsecret: 钉钉应用的 secret，创建应用后获得
        :param agent_id: 钉钉的Agent Id，每个微应用有独立的agent_id，管理员可从后台获得
        :param noncestr: 随机字符串
        :param domain: 域名，可传入随机字符串
        :param callback_url: 回调函数地址，回调函数必须符合check_url方法的要求
        :param aes_key: 用于加解密的aes_key，必须是43为字符串，由大小写字母和数字组成，不能有标点符号
        :param token: 用于回调时生成签名的token，非access_token，传入随机字符串
        """
        # logger
        self.logger = logger
        # 钉钉接口参数
        self.name = name
        self.cache = session_manager
        self.corp_id = corp_id
        self.corp_secret = corp_secret
        self.appkey = appkey
        self.appsecret = appsecret
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
        self.auth = Auth(name=self.name, session_manager=session_manager,
                         corp_id=corp_id, corp_secret=corp_secret,
                         appkey=appkey, appsecret=appsecret)
        # 注册接口方法，为通过run方式调用提供支持
        self.register_methods(auth=self.auth)
        # 其他模块
        self.smartwork = SmartWork(self.auth, self.agent_id, self.logger)
        self.contact = Contact(self.auth, self.logger)
        self.message = Message(self.auth, self.agent_id, self.logger)
        self.file = File(self.auth, self.domain, self.agent_id, self.logger)
        self.customer = Customer(self.auth, self.logger)
        # 忽略回调模块加载异常的情况，仅输出异常日志
        # 主要考虑到windows下安装pycrypto比较繁琐
        try:
            from .callback import CallBack
            self.callback = CallBack(self.auth, self.aes_key, self.token,
                                     self.callback_url, self.corp_id, self.noncestr)
        except BaseException as ex:
            self.logger.error(ex)
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
