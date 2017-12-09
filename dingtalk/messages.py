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


def async_send_msg(access_token, msgtype, agent_id, msgcontent, userid_list=None, dept_id_list=None, to_all_user=False):
    try:
        msgcontent = json.dumps(msgcontent)
    except JSONDecodeError:
        pass
    args = locals().copy()
    payload = {}
    # 请求参数整理
    for k, v in args.items():
        if k in ('msgtype', 'agent_id', 'msgcontent', 'userid_list', 'dept_id_list'):
            if v is not None:
                payload.update({k: v})
    url = get_request_url('dingtalk.corp.message.corpconversation.asyncsend', access_token)
    resp = requests.post(url, data=payload)
    if resp.status_code == 200:
        return resp.json()
    else:
        raise DingTalkExceptions.get_ext_list_err


def get_msg_send_result(access_token, agent_id, task_id):
    url = get_request_url('dingtalk.corp.message.corpconversation.getsendresult', access_token)
    payload = {'task_id': task_id, 'agent_id': agent_id}
    resp = requests.get(url, params=payload)
    if resp.status_code == 200:
        return resp.json()
    else:
        raise DingTalkExceptions.get_ext_list_err


if __name__ == '__main__':
    pass
