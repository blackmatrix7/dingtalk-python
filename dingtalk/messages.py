#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2017/11/30 下午3:02
# @Author : Matrix
# @Github : https://github.com/blackmatrix7/
# @Blog : http://www.cnblogs.com/blackmatrix/
# @File : messages.py
# @Software: PyCharm
import json
import requests
from .foundation import *
from json import JSONDecodeError
from .exceptions import DingTalkExceptions

__author__ = 'blackmatrix'


@dingtalk_resp
def async_send_msg(access_token, msgtype, agent_id, msgcontent, userid_list=None, dept_id_list=None, to_all_user=False):
    try:
        msgcontent = json.dumps(msgcontent)
    except JSONDecodeError:
        pass
    if not isinstance(userid_list, str):
        userid_list = ','.join(userid_list)
    args = locals().copy()
    payload = {}
    # 请求参数整理
    for k, v in args.items():
        if k in ('msgtype', 'agent_id', 'msgcontent', 'userid_list', 'dept_id_list'):
            if v is not None:
                payload.update({k: v})
    resp = call_dingtalk_webapi(access_token, 'dingtalk.corp.message.corpconversation.asyncsend', **payload)
    return resp


@dingtalk_resp
def get_msg_send_result(access_token, agent_id, task_id):
    url = get_request_url(access_token, 'dingtalk.corp.message.corpconversation.getsendresult')
    payload = {'task_id': task_id, 'agent_id': agent_id}
    return requests.get(url, params=payload)


@dingtalk_resp
def get_msg_send_progress(access_token, agent_id, task_id):
    url = get_request_url(access_token, 'dingtalk.corp.message.corpconversation.getsendprogress')
    payload = {'task_id': task_id, 'agent_id': agent_id}
    return requests.get(url, params=payload)


if __name__ == '__main__':
    pass
