#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time: 2018/3/1 上午11:20
# @Author: BlackMatrix
# @Site: https://github.com/blackmatrix7
# @File: __init__.py
# @Software: PyCharm
from .crypto import *
from .callback import *
from functools import partial
from ..exceptions import DingTalkExceptions
from ..foundation import dingtalk_method, get_timestamp

__author__ = 'blackmatrix'

METHODS = {}

method = partial(dingtalk_method, methods=METHODS)


class CallBack:

    def __init__(self, auth, aes_key, token, callback_url, corp_id, noncestr):
        self.access_token = auth.access_token
        self.methods = METHODS
        self.aes_key = aes_key
        self.token = token
        self.callback_url = callback_url
        self.corp_id = corp_id
        self.noncestr = noncestr

    @property
    def timestamp(self):
        return get_timestamp()

    def encrypt(self, plaintext, buf=None):
        """
        钉钉加密数据
        :param plaintext: 明文
        :param buf:
        :return:
        """
        if self.aes_key is None:
            raise RuntimeError('加密解密前需要在初始化DingTalk App时传入aes_key')
        from dingtalk.callback.crypto import encrypt
        ciphertext = encrypt(aes_key=self.aes_key, plaintext=plaintext, key=self.corp_id, buf=buf)
        return ciphertext

    def decrypt(self, ciphertext: str):
        """
        钉钉解密数据
        :param ciphertext: 密文
        :return:
        """
        if self.aes_key is None:
            raise RuntimeError('加密解密前需要在初始化DingTalk App时传入aes_key')
        from dingtalk.callback.crypto import decrypt
        msg, key, buf = decrypt(self.aes_key, ciphertext)
        return msg, key, buf

    def encrypt_text(self, plaintext: str):
        """
        对纯文本进行加密
        :param plaintext: 明文
        :return:
        """
        if self.aes_key is None:
            raise RuntimeError('加密解密前需要在初始化DingTalk App时传入aes_key')
        from dingtalk.callback.crypto import encrypt_text
        ciphertext = encrypt_text(aes_key=self.aes_key, plaintext=plaintext)
        return ciphertext

    def decrypt_text(self, ciphertext: str):
        """
        对纯文本进行解密
        :param ciphertext: 密文
        :return:
        """
        if self.aes_key is None:
            raise RuntimeError('加密解密前需要在初始化DingTalk App时传入aes_key')
        from dingtalk.callback.crypto import decrypt_text
        temp = decrypt_text(self.aes_key, ciphertext)
        return temp

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

    def get_call_back_failed_result(self):
        """
        获取处理失败的钉钉回调
        :return:
        """
        data = get_callback_failed_result(self.access_token)
        return data['failed_list']

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

    def return_success(self):
        """
        钉钉回调需要返回含有success的json，提供一个方法，快速返回一个符合钉钉要求的success json
        :return:
        """
        # 加密success数据
        encrypt_str = self.encrypt('success').decode()
        # 创建时间戳
        timestamp = str(self.timestamp)
        # 获取随机字符串
        nonce = self.noncestr
        # 创建签名
        signature = self.generate_callback_signature(encrypt_str, timestamp, nonce)
        # 返回结果
        return {'msg_signature': signature, 'timeStamp': timestamp, 'nonce': nonce, 'encrypt': encrypt_str}

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
