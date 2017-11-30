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
        self.app = DingTalkApp(name='test',
                               corp_id=current_config.DING_CORP_ID,
                               corp_secret=current_config.DING_CORP_SECRET)

    # 获取 access token
    def test_get_access_token(self):
        access_token = self.app.get_access_token()
        assert access_token is not None

    # 获取 jsapi ticket
    def test_get_jsapi_ticket(self):
        jsapi_ticket = self.app.get_jsapi_ticket()
        assert jsapi_ticket is not None

    # 获取系统标签
    def test_get_label_groups(self):
        label_groups = self.app.get_label_groups()
        return label_groups

    # 获取外部联系人
    def test_get_ext_list(self):
        ext_list = self.app.get_ext_list()
        assert ext_list is not None

    # 新增外部联系人
    def test_add_contact(self):
        # 获取标签
        label_groups = self.app.get_label_groups()
        contact = {'title': '开发工程师',
                   'share_deptids': [],
                   'label_ids': [],
                   'remark': '备注内容',
                   'address': '地址内容',
                   'name': '张三',
                   'follower_userid': '023420013645',
                   'state_code': '86',
                   'company_name': '企业名',
                   'share_userids': ['023420013644'],
                   'mobile': '1308888888'}
        ext_list = self.app.add_corp_ext(contact)
        assert ext_list is not None


if __name__ == '__main__':
    pass
