#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time: 2018/2/28 下午3:31
# @Author: BlackMatrix
# @Site: https://github.com/blackmatrix7
# @File: __init__.py
# @Software: PyCharm
from .space import *
from functools import partial
from ..foundation import dingtalk_method

__author__ = 'blackmatrix'

METHODS = {}

method = partial(dingtalk_method, methods=METHODS)


class File:

    def __init__(self, auth, domain, agent_id):
        self.access_token = auth.access_token
        self.domain = domain
        self.agent_id = agent_id
        self.methods = METHODS

    def get_custom_space(self):
        """
        获取企业下的自定义空间
        https://open-doc.dingtalk.com/docs/doc.htm?spm=a219a.7629140.0.0.Fh7w2d&treeId=373&articleId=104970&docType=1#s2
        :return:
        """
        data = get_custom_space(self.access_token, self.domain, self.agent_id)
        return {'space_id': data['spaceid']}
