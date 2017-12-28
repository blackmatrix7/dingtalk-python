#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2017/12/25 下午3:11
# @Author : Matrix
# @Github : https://github.com/blackmatrix7/
# @Blog : http://www.cnblogs.com/blackmatrix/
# @File : crypto.py
# @Software: PyCharm
import uuid
import struct
import base64
import hashlib
import logging
from Crypto.Cipher import AES

__author__ = 'blackmatrix'


def generate_callback_signature(token: str, ciphertext: str, timestamp: str, nonce: str):
    """
    创建签名
    :param token:
    :param ciphertext: 密文
    :param timestamp:
    :param nonce:
    :return:
    """
    sign = hashlib.sha1(''.join(sorted([token, timestamp, nonce, ciphertext])).encode())
    sign = sign.hexdigest()
    logging.info('signature：' + sign)
    return sign


def check_callback_signature(token, ciphertext, signature, timestamp, nonce):
    """
    验证签名
    算法请访问
    https://open-doc.dingtalk.com/docs/doc.htm?spm=a219a.7386797.0.0.EkauZY&source=search&treeId=366&articleId=107524&docType=1
    :param token: token
    :param ciphertext: 加密后的数据
    :param signature: 签名
    :param timestamp: 时间戳
    :param nonce:
    :return:
    """
    sign = generate_callback_signature(token, ciphertext, timestamp, nonce)
    return sign == signature


def pkcs7_unpad(text):
    """
    删除PKCS#7方式填充的字符串
    :param text:
    :return: str
    """
    return text[0: text.index((text[-1]))]


def pkcs7_pad(multiple, text):
    """
    PKCS#7方式填充字符串
    :param multiple:
    :param text: str
    :return: str
    """
    return text + (multiple - len(text) % multiple) * chr(multiple - len(text) % multiple)


def decrypt_text(aes_key, ciphertext):
    aes_key = base64.b64decode(aes_key + '=')
    ciphertext = base64.b64decode(ciphertext)
    aes = AES.new(aes_key, AES.MODE_CBC, aes_key[:16])
    raw = aes.decrypt(ciphertext)
    raw = pkcs7_unpad(raw)
    return raw


def decrypt(aes_key, ciphertext):
    raw = decrypt_text(aes_key, ciphertext)
    buf = raw[:16].decode().strip()
    length = struct.unpack('!i', raw[16:20])[0]
    msg = raw[20: 20 + length].decode().strip()
    key = raw[20 + length:].decode().strip()
    return msg, key, buf


def encrypt_text(aes_key, plaintext):
    aes_key = base64.b64decode(aes_key + '=')
    aes = AES.new(aes_key, AES.MODE_CBC, aes_key[:16])
    ciphertext = pkcs7_pad(16, plaintext)
    ciphertext = aes.encrypt(ciphertext)
    ciphertext = base64.b64encode(ciphertext)
    return ciphertext


def encrypt(aes_key, plaintext, key, buf=None):
    buf = buf or str(uuid.uuid4()).replace('-', '')
    buf = buf[:16]
    length = struct.pack('!i', len(plaintext)).decode()
    ciphertext = encrypt_text(aes_key, buf + length + plaintext + key)
    return ciphertext

if __name__ == '__main__':
    pass
