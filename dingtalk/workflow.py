#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2017/12/5 上午10:18
# @Author : Matrix
# @Github : https://github.com/blackmatrix7/
# @Blog : http://www.cnblogs.com/blackmatrix/
# @File : workflow.py
# @Software: PyCharm
import json
import requests
from .foundation import *
from datetime import datetime
from .exceptions import DingTalkExceptions

__author__ = 'blackmatrix'

no_value = object()


def create_bpms_instance(access_token, process_code, originator_user_id,
                         dept_id, approvers, form_component_value, agent_id=None,
                         cc_list=None, cc_position='FINISH'):
    """
    发起审批实例
    :param access_token:
    :param process_code:
    :param originator_user_id:
    :param dept_id:
    :param approvers:
    :param form_component_value:
    :param agent_id:
    :param cc_list:
    :param cc_position:
    :return:
    """
    args = locals()
    url = get_request_url('dingtalk.smartwork.bpms.processinstance.create', access_token)
    payload = {}
    for key in ('process_code', 'originator_user_id', 'dept_id', 'approvers', 'form_component_value',
                'agent_id', 'cc_list', 'cc_position'):
        if args.get(key, no_value) is not None:
            payload.update({key: args[key]})
    resp = requests.post(url, data=payload)
    if resp.status_code == 200:
        return resp.json()
    else:
        raise DingTalkExceptions.create_bmps_err


def get_bpms_instance_list(access_token, process_code, start_time, end_time=None, size=10, cursor=0):
    """
    企业可以根据审批流的唯一标识，分页获取该审批流对应的审批实例。只能取到权限范围内的相关部门的审批实例
    :param access_token:
    :param process_code:
    :param start_time:
    :param end_time:
    :param size:
    :param cursor:
    :return:
    """
    start_time = datetime.timestamp(start_time)
    start_time = int(round(start_time * 1000))
    if end_time:
        end_time = datetime.timestamp(end_time)
        end_time = int(round(end_time * 1000))
    args = locals()
    url = get_request_url('dingtalk.smartwork.bpms.processinstance.list', access_token)
    payload = {}
    for key in ('process_code', 'start_time', 'end_time', 'size', 'cursor'):
        if args.get(key, no_value) is not None:
            payload.update({key: args[key]})
    resp = requests.get(url, params=payload)
    if resp.status_code == 200:
        return resp.json()
    else:
        raise DingTalkExceptions.create_bmps_err

if __name__ == '__main__':
    pass
