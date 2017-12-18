#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2017/11/28 下午3:16
# @Author : Matrix
# @Github : https://github.com/blackmatrix7/
# @Blog :
# @File : test_ding.py
# @Software: PyCharm
import json
import unittest
from extensions import cache
from datetime import datetime
from dingtalk import DingTalkApp
from config import current_config
from dateutil.relativedelta import relativedelta
from dingtalk.exceptions import SysException

__author__ = 'blackmatrix'


class DingTalkTestCase(unittest.TestCase):

    def setUp(self):
        self.app = DingTalkApp(name='vcan', cache=cache,
                               agent_id=current_config.DING_AGENT_ID,
                               corp_id=current_config.DING_CORP_ID,
                               corp_secret=current_config.DING_CORP_SECRET)

    # 获取 access token
    def test_get_access_token(self):
        access_token = self.app.get_access_token()
        assert access_token is not None

    # 获取 jsapi ticket
    def test_get_jsapi_ticket(self):
        jsapi_ticket = self.app.get_jsapi_ticket()
        assert jsapi_ticket is not None

    # 获取系统标签
    def test_get_label_groups(self):
        label_groups = self.app.get_label_groups()
        assert label_groups
        label_groups = self.app.run('dingtalk.corp.ext.listlabelgroups', size=20, offset=0)
        assert label_groups
        return label_groups

    # 获取用户
    def test_get_user_list(self):
        dept_list = self.app.get_department_list()
        dept_id = dept_list[0]['id']
        user_list = self.app.get_user_list(dept_id)
        return user_list

    # 获取部门
    def test_get_dempartment_list(self):
        dept_list = self.app.get_department_list()
        return dept_list

    # 获取外部联系人
    def test_get_ext_list(self):
        ext_list = self.app.get_ext_list()
        assert ext_list is not None

    # 新增外部联系人
    def test_add_contact(self):
        # 获取标签
        label_groups = self.app.get_label_groups()
        label_ids = [v for label_group in label_groups for labels in label_group['labels'] for k, v in labels.items() if k == 'id']
        # 获取部门
        dept_list = self.app.get_department_list()
        dept_ids = [dept['id'] for dept in dept_list]
        # 获取用户
        user_list = self.app.get_user_list(dept_ids[0])
        user_ids = [user['userid'] for user in user_list]
        contact = {'title': '开发工程师',
                   'share_deptids': dept_ids[1:3],
                   'label_ids': label_ids[0:3],
                   'remark': '备注内容',
                   'address': '地址内容',
                   'name': '张三',
                   'follower_userid': user_ids[0],
                   'state_code': '86',
                   'company_name': '企业名',
                   'share_userids': user_ids[0:2],
                   'mobile': '13023438888'}
        try:
            result = self.app.add_corp_ext(contact)
            assert result is not None
        except SysException as ex:
            assert '外部联系人已存在' in str(ex)

    # 测试新增工作流实例
    def test_bmps_create(self):
        """
        发起审批流程
        为了避免频繁发起审批流程，默认不执行此测试用例
        :return:
        """
        assert self.app.access_token
        # args = {'process_code': 'PROC-FF6Y4BE1N2-B3OQZGC9RLR4SY1MTNLQ1-91IKFUAJ-4',
        #         'originator_user_id': '112322273839908294',
        #         'dept_id': '49381153',
        #         'approvers': ['112322273839908294'],
        #         'form_component_values': [{'value': '哈哈哈哈', 'name': '姓名'},
        #                                   {'value': '哈哈哈哈', 'name': '部门'},
        #                                   {'value': '哈哈哈哈', 'name': '加班事由'}]}
        # resp = self.app.create_bpms_instance(**args)
        # assert resp

    # 测试获取工作流实例列表
    def test_bpms_list(self):
        """

        刚刚发起流程时，返回情况
        **********************
        [
            {'title': '阿三的测试流程',
             'originator_dept_id': '49381153',
             'approver_userid_list': {'string': ['112322273839908294']},
             'status': 'RUNNING',
             'process_instance_id': 'a97b96c4-6e91-40a7-9e74-658224dd5c1a',
             'originator_userid': '112322273839908294',
             'create_time': '2017-12-06 10:28:19',
             'process_instance_result': '',
             'form_component_values':
                 {'form_component_value_vo':
                     [{'value': '哈哈哈哈', 'name': '姓名'},
                      {'value': '哈哈哈哈', 'name': '部门'},
                      {'value': '哈哈哈哈', 'name': '加班事由'}]
                 }
            }
        ]
        第一次审批同意时
        **********************
        [
            {'create_time': '2017-12-06 10:28:19',
             'originator_dept_id': '49381153',
             'process_instance_id': 'a97b96c4-6e91-40a7-9e74-658224dd5c1a',
             'approver_userid_list': {'string': ['112322273839908294']},
             'title': '阿三的测试流程',
             'status': 'RUNNING',
             'process_instance_result': 'agree',
             'form_component_values':
                 {'form_component_value_vo':
                     [{'value': '哈哈哈哈', 'name': '姓名'},
                      {'value': '哈哈哈哈', 'name': '部门'},
                      {'value': '哈哈哈哈', 'name': '加班事由'}]
                 },
             'originator_userid': '112322273839908294'}
        ]
        第二次审批同意时
        **********************
        [
            {'create_time': '2017-12-06 10:28:19',
             'approver_userid_list': {'string': ['112322273839908294']},
             'process_instance_result': 'agree',
             'form_component_values':
                {'form_component_value_vo':
                    [{'name': '姓名', 'value': '哈哈哈哈'},
                     {'name': '部门', 'value': '哈哈哈哈'},
                     {'name': '加班事由', 'value': '哈哈哈哈'}]},
             'process_instance_id': 'a97b96c4-6e91-40a7-9e74-658224dd5c1a',
             'originator_dept_id': '49381153',
             'title': '阿三的测试流程',
             'status': 'RUNNING',
             'originator_userid': '112322273839908294'}]}
        最后一次审批通过时
        **********************
        [
            {'create_time': '2017-12-06 10:28:19',
             'process_instance_result': 'agree',
             'status': 'COMPLETED',
             'process_instance_id': 'a97b96c4-6e91-40a7-9e74-658224dd5c1a',
             'title': '阿三的测试流程',
             'originator_userid': '112322273839908294',
             'originator_dept_id': '49381153',
             'approver_userid_list': {'string': ['112322273839908294']},
             'form_component_values':
                {'form_component_value_vo':
                    [{'name': '姓名', 'value': '哈哈哈哈'},
                     {'name': '部门', 'value': '哈哈哈哈'},
                     {'name': '加班事由', 'value': '哈哈哈哈'}]},
             'finish_time': '2017-12-06 10:41:54'
            }
        ]
        :return:
        """
        start_date = datetime.now() - relativedelta(month=1)
        data = self.app.get_bpms_instance_list(process_code='PROC-FF6Y4BE1N2-B3OQZGC9RLR4SY1MTNLQ1-91IKFUAJ-4',
                                               start_time=start_date)
        assert data

    # 测试钉钉实例绑定的方法
    def test_dingtalk_methods(self):
        methods = self.app.methods
        assert methods

    def test_async_send_msg(self):
        """
        测试异步发送消息
        为了避免频繁发送消息，默认不运行测试用例
        :return:
        """
        assert self.app.access_token
        # # 获取部门
        # dept_list = self.app.get_department_list()
        # dept_ids = [dept['id'] for dept in dept_list]
        # # 获取用户
        # user_list = self.app.get_user_list(dept_ids[1])
        # user_ids = [user['userid'] for user in user_list]
        # data = self.app.async_send_msg(msgtype='text', userid_list=user_ids,
        #                                msgcontent={'content': '现在为您报时，北京时间 {}'.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))})
        # assert data
        # for item in data['success_userid_list']:
        #     task_id = item['task_id']
        #     assert task_id
        #     result = self.app.get_msg_send_result(task_id)
        #     assert result

    # 测试获取用户信息
    def test_get_user_info(self):
        # 获取部门
        dept_list = self.app.get_department_list()
        dept_ids = [dept['id'] for dept in dept_list]
        # 获取用户
        user_list = self.app.get_user_list(dept_ids[1])
        user_id = [user['userid'] for user in user_list][0]
        data = self.app.get_user_info(user_id=user_id)
        assert data

    def test_user_operator(self):
        dept_list = self.app.get_department_list()
        dept_id = None
        for dept in dept_list:
            if dept['name'] == '信息部':
                dept_id = dept['id']
                break
        if dept_id is None:
            dept_id = dept_list[1]
        user_info = {
            'name': '马小云',
            'orderInDepts': {dept_id: 8},
            'department': [dept_id],
            'position': '马云，你不认识？？！！',
            'mobile': '13058888882'
        }
        result = self.app.create_user(**user_info)
        assert result
        user_id = result['userid']
        new_user_info = {
            'userid': user_id,
            'name': '马小云',
            'orderInDepts': {dept_id: 8},
            'department': [dept_id],
            'position': '我就是马小云！！！',
            'mobile': '13058888882'
        }
        result = self.app.update_user(**new_user_info)
        assert result
        result = self.app.delete_user(userid=user_id)
        assert result

    #
    def test_get_dept_info(self):
        # 获取部门详情
        dept_list = self.app.get_department_list()
        dept_id = dept_list[1]['id']
        resp = self.app.get_department(dept_id)
        assert resp

    def test_dept_operator(self):
        dept_info = {
            'name': '霍格沃茨魔法学校',
            'parentid': 1
        }
        dept_id = self.app.create_department(**dept_info)
        assert dept_id
        new_dept_info = {
            'id': dept_id,
            'name': '霍格沃茨魔法学校：格兰芬多',
            'parentid': 1
        }
        dept = self.app.update_department(**new_dept_info)
        assert dept
        dept_list = self.app.get_department_list()
        assert dept_list
        for dept in dept_list:
            if '霍格沃茨魔法学校' in dept['name']:
                dept_id = dept['id']
                result = self.app.delete_department(dept_id)
                assert result

    def test_get_user_depts(self):
        # 获取部门
        dept_list = self.app.get_department_list()
        dept_ids = [dept['id'] for dept in dept_list]
        # 获取用户
        user_list = self.app.get_user_list(dept_ids[1])
        user_id = [user['userid'] for user in user_list][1]
        depts = self.app.get_user_departments(user_id)
        assert depts

    def test_get_org_user_count(self):
        result = self.app.get_org_user_count(0)
        assert result > 1
        result = self.app.get_org_user_count(1)
        assert result > 1

    def test_corp_role_list(self):
        result = self.app.get_corp_role_list()
        assert result

    def test_get_all_corp_role_list(self):
        result = self.app.get_all_corp_role_list()
        assert result

    def test_get_role_simple_list(self):
        role_group_list = self.app.get_all_corp_role_list()
        role_id_list = [v for role_group in role_group_list for role in role_group['roles'] for k, v in role.items() if k == 'id']
        user_id_list = []
        for role_id in role_id_list:
            user = self.app.get_role_simple_list(role_id=role_id) or []
            user_id_list.extend(user)
        assert user_id_list

    def test_sign(self):
        jsapi_ticket = 'raj3X1Z2OIYqxuQ29WVK1uvhIvrsXC4qPwYE1KQ174zx7MfhX2qHKdtFE2XdUxbdp1WfoctcNCmBfbfYEJj5um'
        noncestr = 'abcdefg'
        timestamp = '1440678945'
        url = 'http://调用jsapi页面'
        sign = self.app.sign(jsapi_ticket=jsapi_ticket, noncestr=noncestr, timestamp=timestamp, url=url)
        assert sign == '750d0719eeb810f6fa12b04d87d0d7789c4bc64f'


