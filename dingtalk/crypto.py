#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2017/12/25 下午3:11
# @Author : Matrix
# @Github : https://github.com/blackmatrix7/
# @Blog : http://www.cnblogs.com/blackmatrix/
# @File : crypto.py
# @Software: PyCharm
import json
import base64
import hashlib
from Crypto.Cipher import AES

__author__ = 'blackmatrix'


def generate_signature(access_token, encrypt, timestamp, nonce):
    sign = hashlib.sha1(''.join(sorted([access_token, timestamp, nonce, encrypt])).encode())
    return sign.hexdigest()


def check_signature(access_token, encrypt, signature, timestamp, nonce):
    sign = generate_signature(access_token, encrypt, timestamp, nonce)
    return sign == signature


def decrypt(aes_key, encrypt):
    aes_key = base64.b64decode(aes_key + '=')
    encrypt = base64.b64decode(encrypt)
    aes = AES.new(aes_key, AES.MODE_CBC, aes_key[:16])
    raw = aes.decrypt(encrypt).decode('utf-8')
    raw = raw[raw.index('{'): raw.rindex('}') + 1]
    raw = json.loads(raw)
    return raw


if __name__ == '__main__':
    pass
