#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time: 2018/2/28 上午10:41
# @Author: BlackMatrix
# @Site: https://github.com/blackmatrix7
# @File: smartwork
# @Software: PyCharm
from .foundation import call_dingtalk_webapi, dingtalk_resp

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


if __name__ == '__main__':
    pass
