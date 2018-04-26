#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time: 2018/2/28 下午2:45
# @Author: BlackMatrix
# @Site: https://github.com/blackmatrix7
# @File: __init__.py
# @Software: PyCharm
import logging
from .conversation import *
from functools import partial
from ..foundation import dingtalk_method

__author__ = 'blackmatrix'

METHODS = {}

method = partial(dingtalk_method, methods=METHODS)


class Message:

    methods = {}

    def __init__(self, auth, agent_id, logger=logging):
        self.auth = auth
        self.agent_id = agent_id
        self.logger = logger

    @method('dingtalk.corp.message.corpconversation.asyncsend')
    def async_send_msg(self, msgtype, msgcontent, userid_list=None, dept_id_list=None, to_all_user=False):
        """
        异步发送消息
        接口文档：
        https://open-doc.dingtalk.com/docs/doc.htm?spm=a219a.7629140.0.0.C50a1Y&treeId=374&articleId=28915&docType=2
        消息内容格式说明：
        https://open-doc.dingtalk.com/docs/doc.htm?spm=a219a.7629140.0.0.CToLEy&treeId=374&articleId=104972&docType=1
        :param msgtype: 消息类型
        :param msgcontent: 消息内容
        :param userid_list: 发送的用户列表
        :param dept_id_list: 发送的部门列表
        :param to_all_user: 是否全员发送（全员发送有次数限制）
        :return:
        """
        # 接口返回结果列表，每次发送只能发送20个userid，超出后需要分多次发送
        result_list = []
        userid_group_list = [userid_list[i: i+20] for i in range(0, len(userid_list), 20)]
        for userid_group in userid_group_list:
            resp = async_send_msg(access_token=self.auth.access_token, agent_id=self.agent_id, msgtype=msgtype,
                                  userid_list=userid_group, dept_id_list=dept_id_list, to_all_user=to_all_user,
                                  msgcontent=msgcontent)
            result = {'request_id': resp['dingtalk_corp_message_corpconversation_asyncsend_response']['request_id'],
                      'task_id': resp['dingtalk_corp_message_corpconversation_asyncsend_response']['result']['task_id'],
                      'success': resp['dingtalk_corp_message_corpconversation_asyncsend_response']['result']['success']}
            result_list.append(result)
        return result_list

    @method(method_name='dingtalk.corp.message.corpconversation.getsendresult')
    def get_msg_send_result(self, task_id, agent_id=None):
        """
        获取消息发送结果
        接口文档：
        https://open-doc.dingtalk.com/docs/doc.htm?spm=a219a.7629140.0.0.QvhuFr&treeId=374&articleId=28918&docType=2
        :param task_id: 发送消息时返回的task_id
        :param agent_id: 应用id
        :return:
        """
        agent_id = agent_id or self.agent_id
        resp = get_msg_send_result(self.auth.access_token, agent_id, task_id)
        return {'request_id': resp['dingtalk_corp_message_corpconversation_getsendresult_response']['request_id'],
                'send_result': resp['dingtalk_corp_message_corpconversation_getsendresult_response']['result']['send_result'],
                'success': resp['dingtalk_corp_message_corpconversation_getsendresult_response']['result']['success']}

    @method(method_name='dingtalk.corp.message.corpconversation.getsendprogress')
    def get_msg_send_progress(self, task_id, agent_id=None):
        """
        获取企业发送消息进度
        接口文档：
        https://open-doc.dingtalk.com/docs/doc.htm?spm=a219a.7629140.0.0.68Lh70&treeId=374&articleId=28917&docType=2
        :param task_id: 发送消息时返回的task_id
        :param agent_id: 应用id
        :return:
        """
        agent_id = agent_id or self.agent_id
        resp = get_msg_send_progress(self.auth.access_token, agent_id, task_id)
        return {'request_id': resp['dingtalk_corp_message_corpconversation_getsendprogress_response']['request_id'],
                'progress': resp['dingtalk_corp_message_corpconversation_getsendprogress_response']['result']['progress'],
                'success': resp['dingtalk_corp_message_corpconversation_getsendprogress_response']['result']['success']}
