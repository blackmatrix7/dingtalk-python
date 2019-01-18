#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time: 2018/2/28 上午10:41
# @Author: BlackMatrix
# @Site: https://github.com/blackmatrix7
# @File: smartwork
# @Software: PyCharm
import requests
from datetime import datetime
from ..apis import DING_ATTENDANCE_RECORD_LIST
from ..foundation import call_dingtalk_webapi, dingtalk_resp

__author__ = 'blackmatrix'


@dingtalk_resp
def get_schedule_list(access_token, work_date, offset=0, size=200):
    """
    考勤排班信息按天全量查询接口
    :param access_token:
    :param work_date:
    :param offset:
    :param size:
    :return:
    """
    return call_dingtalk_webapi(access_token, 'dingtalk.smartwork.attends.listschedule',
                                'GET', work_date=work_date, offset=offset, size=size)


@dingtalk_resp
def get_simple_groups(access_token, offset=0, size=10):
    """
    获取考勤组列表详情
    :param access_token:
    :param offset: 偏移位置
    :param size: 分页大小，最大10
    :return:
    """
    return call_dingtalk_webapi(access_token, 'dingtalk.smartwork.attends.getsimplegroups',
                                'GET', offset=offset, size=size)


@dingtalk_resp
def get_attendance_record_list(access_token, user_ids, check_data_from, check_data_to):
    """

    :param access_token:
    :param user_ids:
    :param check_data_from:
    :param check_data_to:
    :return:
    """
    try:
        check_data_from = datetime.strftime(check_data_from, '%Y-%m-%d %H:%M:%S')
    except AttributeError:
        pass
    try:
        check_data_to = datetime.strftime(check_data_to, '%Y-%m-%d %H:%M:%S')
    except AttributeError:
        pass
    payload = {'userIds': user_ids, 'checkDateFrom': check_data_from, 'checkDateTo': check_data_to}
    url = DING_ATTENDANCE_RECORD_LIST.format(access_token=access_token)
    resp = requests.post(url, json=payload)
    return resp


if __name__ == '__main__':
    pass
