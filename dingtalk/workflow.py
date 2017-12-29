#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2017/12/5 上午10:18
# @Author : Matrix
# @Github : https://github.com/blackmatrix7/
# @Blog : http://www.cnblogs.com/blackmatrix/
# @File : workflow.py
# @Software: PyCharm
import json
from .foundation import *
from datetime import datetime
from json import JSONDecodeError

__author__ = 'blackmatrix'

no_value = object()


@dingtalk_resp
def create_bpms_instance(access_token, process_code, originator_user_id,
                         dept_id, approvers, form_component_values, agent_id=None,
                         cc_list=None, cc_position='FINISH'):
    """
    发起审批实例
    :param access_token:
    :param process_code: 
    :param originator_user_id: 流程发起人id
    :param dept_id: 流程发起人所在部门id，如果流程发起人不属于此部门，会出现异常
    :param approvers: 审批人，传入一个列表，会依次审批
    :param form_component_values:
    :param agent_id:
    :param cc_list:
    :param cc_position:
    :return:
    """
    # 需要将form_component_values转换成json字符串
    try:
        form_component_values = json.dumps(form_component_values)
    except JSONDecodeError:
        pass
    # 钉钉传入的userid，是以,分隔的字符串
    approvers = ','.join(approvers)
    args = locals()
    payload = {}
    for key in ('process_code', 'originator_user_id', 'dept_id', 'approvers', 'form_component_values',
                'agent_id', 'cc_list', 'cc_position'):
        if args.get(key) is not None:
            payload.update({key: args[key]})
    resp = call_dingtalk_webapi(access_token, 'dingtalk.smartwork.bpms.processinstance.create', **payload)
    return resp


@dingtalk_resp
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
    url = get_request_url(access_token, 'dingtalk.smartwork.bpms.processinstance.list')
    payload = {}
    for key in ('process_code', 'start_time', 'end_time', 'size', 'cursor'):
        if args.get(key, no_value) is not None:
            payload.update({key: args[key]})
    return requests.get(url, params=payload)

if __name__ == '__main__':
    pass
