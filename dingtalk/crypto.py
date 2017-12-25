#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2017/12/25 下午3:11
# @Author : Matrix
# @Github : https://github.com/blackmatrix7/
# @Blog : http://www.cnblogs.com/blackmatrix/
# @File : crypto.py
# @Software: PyCharm
import base64
import hashlib
__author__ = 'blackmatrix'


def generate_signature(access_token, encrypt, timestamp, nonce):
    raw = hashlib.sha1(''.join(sorted([access_token, timestamp, nonce, encrypt])).encode())
    return raw.hexdigest()


def check_signature(access_token, encrypt, signature, timestamp, nonce):
    raw = generate_signature(access_token, encrypt, timestamp, nonce)
    return raw == signature


if __name__ == '__main__':
    pass
