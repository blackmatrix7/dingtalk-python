#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2017/11/28 下午3:16
# @Author : Matrix
# @Github : https://github.com/blackmatrix7/
# @Blog : http://www.cnblogs.com/blackmatrix/
# @File : test_ding.py
# @Software: PyCharm
import unittest
from dingtalk import DingTalkApp
from config import current_config
from dingtalk.authentication import get_access_token

__author__ = 'blackmatrix'


class DingTalkTestCase(unittest.TestCase):

    def setUp(self):
        self.app = DingTalkApp(name='test')

    # 获取 access token
    def test_get_access_token(self):
        access_token = self.app.get_access_token()
        assert access_token is not None

    # 获取 jsapi ticket
    def test_get_jsapi_ticket(self):
        jsapi_ticket = self.app.get_jsapi_ticket()
        assert jsapi_ticket is not None



if __name__ == '__main__':
    pass
