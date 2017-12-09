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
    url = get_request_url('dingtalk.corp.message.corpconversation.asyncsend', access_token)
    # 请求参数整理
    for k, v in args.items():
        if k in ('msgtype', 'agent_id', 'msgcontent', 'userid_list', 'dept_id_list'):
            if v is not None:
                payload.update({k: v})
    # 钉钉的企业通知接口似乎存在bug，当向对个user_id推送时，只有第一个user_id可以收到消息
    # 暂时的解决方案，将userid_list拆开单独请求
    result = {'success_userid_list': [], 'failed_userid_list': []}
    for user_id in userid_list:
        payload['userid_list'] = [user_id]
        resp = requests.post(url, data=payload)
        if resp.status_code == 200:
            resp = resp.json()
            task_id = resp['dingtalk_corp_message_corpconversation_asyncsend_response']['result']['task_id']
            result['success_userid_list'].append({'user_id': user_id, 'task_id': task_id})
        else:
            result['failed_userid_list'].append({'user_id': user_id})
    return result


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
