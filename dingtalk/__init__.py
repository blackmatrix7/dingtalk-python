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
from .smartwork import SmartWork
from operator import methodcaller
from .exceptions import DingTalkExceptions
from .foundation import get_timestamp, retry
from .callback import register_callback, get_callback_failed_result, update_callback

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


class BaseDingTalkApp:

    """
    钉钉超类，鉴权模块在此处进行实例化
    """

    def __init__(self, name, session_manager, corp_id, corp_secret, agent_id=None,
                 noncestr=None, domain=None, callback_url=None, aes_key=None,
                 token=None):
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
        # 钉钉配置
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
        # 钉钉接口模块
        # 鉴权模块需要先创建，否则后续其他模块的实例化会出现异常
        self.auth = Auth(name=self.name, session_manager=session_manager, corp_id=corp_id, corp_secret=corp_secret)
        # 注册接口方法，为通过run方式调用提供支持
        self.register_methods(auth=self.auth)
        # 其他参数
        self.methods = {}

    def register_methods(self, **modules):
        for module_name, module_obj in modules.items():
            for method_name, func_name in module_obj.methods.items():
                self.methods.update({method_name: {'module': module_name, 'func': func_name}})

    def get_access_token(self):
        """
        在缓存中设置access token 7000秒过期，每次过期会自动重新获取 access token
        :return:
        """
        return self.auth.get_access_token()

    def refresh_access_token(self, time_out=7000):
        """
        刷新access_token
        :return:
        """
        return self.auth.refresh_access_token(time_out=time_out)

    @property
    def access_token(self):
        return self.auth.get_access_token()

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


class DingTalkApp(BaseDingTalkApp):

    def __init__(self, name, session_manager, corp_id, corp_secret, agent_id=None,
                 noncestr=None, domain=None, callback_url=None, aes_key=None,
                 token=None):
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
        self.aes_key = aes_key or 'gbDjdBRfcxrwQA7nSFELj9c0HoWUpcfg8YURx7G84YI'
        self.token = token or 'LnPxMAp7doy'
        self.domain = domain or 'A2UOM1pZOxQ'
        self.noncestr = noncestr or 'VCFGKFqgRA3xtYEhvVubdRY1DAvzKQD0AliCViy'
        # 调用超类的初始化方法，主要用于实现钉钉鉴权
        # 鉴权模块需要先创建，否则后续其他模块的实例化会出现异常
        super().__init__(name=name, session_manager=session_manager, corp_id=corp_id, corp_secret=corp_secret,
                         agent_id=agent_id, noncestr=noncestr, domain=domain, callback_url=callback_url,
                         aes_key=aes_key, token=token)
        # 钉钉接口模块
        self.smartwork = SmartWork(self.access_token, self.agent_id)
        self.contact = Contact(self.access_token)
        self.message = Message(self.access_token, self.agent_id)
        self.file = File(self.access_token, self.domain, self.agent_id)
        self.customer = Customer(self.access_token)
        # 注册接口方法，为通过run方式调用提供支持
        self.register_methods(smartwork=self.smartwork, contact=self.contact, message=self.message,
                              file=self.file, customer=self.customer)

    @property
    def space_id(self):
        """
        获取space id
        https://open-doc.dingtalk.com/docs/doc.htm?spm=a219a.7629140.0.0.Fh7w2d&treeId=373&articleId=104970&docType=1#s2
        :return:
        """
        data = self.file.get_custom_space()
        return data['space_id']

    def register_callback(self, callback_tag):
        """
        向钉钉注册回调接口，只能注册一次，后续需要修改，请调用更新回调接口
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
        """
        向钉钉更新回调接口
        只能在注册回调接口后使用
        :param callback_tag:
        :return:
        """
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
