#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time: 2018/2/28 下午1:49
# @Author: BlackMatrix
# @Site: https://github.com/blackmatrix7
# @File: __init__.py
# @Software: PyCharm
from datetime import datetime
from ..exceptions import DingTalkExceptions
from .workflow import get_bpms_instance_list
from .attends import get_attendance_record_list, get_simple_groups, get_schedule_list

__author__ = 'blackmatrix'


class SmartWork:

    def __init__(self, access_token):
        self.access_token = access_token

    def get_schedule_list(self, work_date, offset=0, size=200):
        """
        考勤排班信息按天全量查询接口
        https://open-doc.dingtalk.com/docs/doc.htm?spm=a219a.7629140.0.0.ZoLh71&treeId=385&articleId=29082&docType=2
        :param work_date:
        :param offset:
        :param size:
        :return:
        """
        try:
            work_date = work_date.strftime('%Y-%m-%d %H:%M:%S')
        except AttributeError:
            pass
        result = get_schedule_list(self.access_token, work_date, offset, size)
        data = {
            'request_id': result['dingtalk_smartwork_attends_listschedule_response']['request_id'],
            'schedules': result['dingtalk_smartwork_attends_listschedule_response']['result']['result']['schedules']['at_schedule_for_top_vo'],
            'has_more': result['dingtalk_smartwork_attends_listschedule_response']['result']['result']['has_more']
        }
        return data

    def get_simple_groups(self, offset=0, size=10):
        """
        获取考勤组列表详情
        https://open-doc.dingtalk.com/docs/doc.htm?spm=a219a.7629140.0.0.OIXvT4&treeId=385&articleId=29083&docType=2
        :param offset:
        :param size:
        :return:
        """
        result = get_simple_groups(self.access_token, offset, size)
        data = {'request_id': result['dingtalk_smartwork_attends_getsimplegroups_response']['request_id'],
                'has_more': result['dingtalk_smartwork_attends_getsimplegroups_response']['result']['result']['has_more'],
                'groups': result['dingtalk_smartwork_attends_getsimplegroups_response']['result']['result']['groups']['at_group_for_top_vo']}
        return data

    def get_attendance_record_list(self, user_ids, check_data_from, check_data_to):
        """
        获取考勤打卡记录
        :param user_ids: 企业内的员工id列表，最多不能超过50个
        :param check_data_from: 查询考勤打卡记录的起始工作日
        :param check_data_to: 查询考勤打卡记录的结束工作日。注意，起始与结束工作日最多相隔7天
        :return:
        """
        result = get_attendance_record_list(self.access_token, user_ids, check_data_from, check_data_to)
        # 钉钉接口返回的数据没有request_id 2018.02.28
        return result

    def get_bpms_instance_list(self, process_code, start_time, end_time=None, size=10, cursor=0):
        """

        :param process_code:
        :param start_time:
        :param end_time:
        :param size: 每次获取的记录条数，最大只能是10
        :param cursor:
        :return:
        """
        data = get_bpms_instance_list(self.access_token, process_code, start_time, end_time, size, cursor)
        instance_list = data['dingtalk_smartwork_bpms_processinstance_list_response']['result']['result']['list'].get('process_instance_top_vo', [])
        next_cursor = data['dingtalk_smartwork_bpms_processinstance_list_response']['result']['result'].get('next_cursor', 0)
        return {'request_id': data['dingtalk_smartwork_bpms_processinstance_list_response']['request_id'],
                'success': data['dingtalk_smartwork_bpms_processinstance_list_response']['result']['success'],
                'instance_list': instance_list,
                'next_cursor': next_cursor}

    def get_all_bpms_instance_list(self, process_code, start_time, end_time=None):
        """
        获取"全部"审批实例
        :param process_code:
        :param start_time: 起始时间，如果不传，默认当前时间往前推6个月
        :param end_time: 结束时间，如果不传，默认当前时间
        :return:
        """
        now = datetime.now()
        end_time = end_time or now
        if start_time > now or start_time > end_time:
            raise DingTalkExceptions.timestamp_err('起始时间不能晚于当前时间或结束时间')
        size = 10
        cursor = 0
        bpms_instance_list = []
        request_id = {}
        while True:
            result = self.get_bpms_instance_list(process_code, start_time, end_time=end_time, size=size, cursor=cursor)
            request_id.update({result['request_id']: {'success': result['success']}})
            bpms_instance_list.extend(result['instance_list'])
            if result['next_cursor'] > 0:
                cursor = result['next_cursor']
            else:
                break
        return {'request_id': request_id, 'bpms_instance_list': bpms_instance_list}

if __name__ == '__main__':
    pass
