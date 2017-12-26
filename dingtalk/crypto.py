#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2017/12/25 下午3:11
# @Author : Matrix
# @Github : https://github.com/blackmatrix7/
# @Blog : http://www.cnblogs.com/blackmatrix/
# @File : crypto.py
# @Software: PyCharm
import json
import uuid
import struct
import base64
import hashlib
from Crypto.Cipher import AES

__author__ = 'blackmatrix'


def generate_signature(access_token, encrypt_text, timestamp, nonce):
    sign = hashlib.sha1(''.join(sorted([access_token, timestamp, nonce, encrypt_text])).encode())
    return sign.hexdigest()


def check_signature(access_token, encrypt_text, signature, timestamp, nonce):
    sign = generate_signature(access_token, encrypt_text, timestamp, nonce)
    return sign == signature


def decrypt(aes_key, encrypt_text):
    aes_key = base64.b64decode(aes_key + '=')
    encrypt_text = base64.b64decode(encrypt_text)
    aes = AES.new(aes_key, AES.MODE_CBC, aes_key[:16])
    raw = aes.decrypt(encrypt_text).decode('utf-8')
    data = raw[raw.index('{'): raw.rindex('}') + 1]
    key = raw[raw.rindex('}') + 1:]
    buf = raw[:raw.rindex('{')]
    return data, key, buf


def encrypt(aes_key, plaintext, key, buf=None):
    aes_key = base64.b64decode(aes_key + '=')
    buf = buf or str(uuid.uuid4()).replace('-', '')
    buf = buf[:16]
    length = struct.pack('!i', len(plaintext)).decode()
    aes = AES.new(aes_key, AES.MODE_CBC, aes_key[:16])
    encrypt_text = aes.encrypt(buf + length + plaintext + key)
    encrypt_text = base64.b64encode(encrypt_text)
    return encrypt_text


if __name__ == '__main__':
    pass
