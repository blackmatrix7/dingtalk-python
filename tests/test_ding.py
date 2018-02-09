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
from dingtalk.crypto import *
from datetime import datetime
from dingtalk import DingTalkApp
from config import current_config
from extensions import session_manager
from dingtalk.exceptions import DingTalkException

__author__ = 'blackmatrix'


class DingTalkTestCase(unittest.TestCase):

    def setUp(self):
        self.app = DingTalkApp(name='vcan', session_manager=session_manager,
                               agent_id=current_config.DING_AGENT_ID,
                               corp_id=current_config.DING_CORP_ID,
                               corp_secret=current_config.DING_CORP_SECRET,
                               aes_key='4g5j64qlyl3zvetqxz5jiocdr586fn2zvjpa8zls3ij')

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
        all_label_groups = self.app.get_all_label_groups()
        assert all_label_groups

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
        label_ids = [str(v) for label_group in label_groups for labels in label_group['labels'] for k, v in labels.items() if k == 'id']
        # label_ids = '[{}]'.format(','.join(label_ids[4: 7]))
        label_ids = label_ids[4: 7]
        # 获取部门
        dept_list = self.app.get_department_list()
        dept_ids = [dept['id'] for dept in dept_list]
        # 获取用户
        user_list = self.app.get_user_list(dept_ids[1])
        user_ids = [user['userid'] for user in user_list]
        contact = {
            # 'title': 'master',
            # 'share_deptids': dept_ids[2:4],
            'label_ids': [265253444, 264113195],
            # 'remark': 'nonting',
            # 'address': 'KungFuPanda',
            'name': 'shifu',
            'follower_userid': '2741125726502831',
            'state_code': '86',
            # 'company_name': 'KungFuPanda',
            # 'share_userids': user_ids[2:6],
            'mobile': '18605203032'
        }
        try:
            result = self.app.add_corp_ext(contact)
            assert result is not None
        except DingTalkException as ex:
            assert '外部联系人已存在' in str(ex)

    # 测试新增工作流实例
    def test_bmps_create(self):
        """
        发起审批流程
        为了避免频繁发起审批流程，默认不执行此测试用例
        :return:
        """
        assert self.app.access_token
        # 获取部门
        dept_list = self.app.get_department_list()
        dept_ids = [dept['id'] for dept in dept_list]
        # 测试部门
        originator_dept_id = dept_ids[1]
        # 获取用户
        originator_user_list = self.app.get_user_list(originator_dept_id)
        originator_user_id = [user['userid'] for user in originator_user_list][0]
        args = {'process_code': 'PROC-FF6Y4BE1N2-B3OQZGC9RLR4SY1MTNLQ1-91IKFUAJ-4',
                'originator_user_id': originator_user_id,
                'dept_id': originator_dept_id,
                'approvers': ['05273640343597xc66032', '11232227383990829d4', '11232227561147d773'],
                'form_component_values': [{'value': '哈哈哈哈', 'name': '姓名'},
                                          {'value': '哈哈哈哈', 'name': '部门'},
                                          {'value': '哈哈哈哈', 'name': '加班事由'}]}
        try:
            # 测试错误情况
            resp = self.app.create_bpms_instance(**args)
            assert resp
        except BaseException as ex:
            assert '审批实例参数错误，具体可能为:发起人、审批人、抄送人的userid错误，发起部门id错误，发起人不在发起部门中' in str(ex)
        dev_dept_id = dept_ids[1]
        dev_user_list = self.app.get_user_list(dev_dept_id)
        approvers = [user['userid'] for user in dev_user_list]
        args = {'process_code': 'PROC-FF6Y4BE1N2-B3OQZGC9RLR4SY1MTNLQ1-91IKFUAJ-4',
                'originator_user_id': originator_user_id,
                'dept_id': originator_dept_id,
                'approvers': approvers,
                'form_component_values': [{'value': '哈哈哈哈', 'name': '姓名'},
                                          {'value': '哈哈哈哈', 'name': '部门'},
                                          {'value': '哈哈哈哈', 'name': '加班事由'}]}
        resp = self.app.create_bpms_instance(**args)
        assert resp

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
        assert self.app.access_token
        start_time = datetime(year=2017, month=6, day=1, hour=1, minute=1, second=1, microsecond=1)
        data = self.app.get_bpms_instance_list(process_code='PROC-FF6Y4BE1N2-B3OQZGC9RLR4SY1MTNLQ1-91IKFUAJ-4',
                                               start_time=start_time)
        assert data
        # 测试错误情况，传入一个不存在的process_code
        data = self.app.get_bpms_instance_list(process_code='PROC-XXXXXXXX-XXXXXXXX-XXXXXXX-X',
                                               start_time=start_time)
        assert len(data['instance_list']) == 0

    # 获取全部工作流实例
    def test_all_bpms_list(self):
        start_time = datetime(year=2017, month=6, day=1, hour=1, minute=1, second=1, microsecond=1)
        data = self.app.get_all_bpms_instance_list(process_code='PROC-FF6Y4BE1N2-B3OQZGC9RLR4SY1MTNLQ1-91IKFUAJ-4',
                                                   start_time=start_time)
        assert data is not None

    # 测试钉钉实例绑定的方法
    def test_dingtalk_methods(self):
        methods = self.app.methods
        assert methods

    # # 异步发送消息
    # def test_async_send_msg(self):
    #     """
    #     测试异步发送消息
    #     :return:
    #     """
    #     assert self.app.access_token
    #     # 获取部门
    #     dept_list = self.app.get_department_list()
    #     dept_ids = [dept['id'] for dept in dept_list]
    #     # 获取用户
    #     user_list = self.app.get_user_list(dept_ids[1])
    #     user_ids = [user['userid'] for user in user_list]
    #     # 测试错误的情况，错误的msgtype
    #     try:
    #         data = self.app.async_send_msg(msgtype='text2', userid_list=user_ids,
    #                                        msgcontent={'content': '现在为您报时，北京时间 {}'.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))})
    #         assert data
    #     except BaseException as ex:
    #         assert '不合法的消息类型' in str(ex)
    #     # 测试正确的情况，避免频繁发送消息，通常不运行此测试
    #     data = self.app.async_send_msg(msgtype='text', userid_list=user_ids,
    #                                    msgcontent={'content': '现在为您报时，北京时间 {}'.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))})
    #     assert data
    #     task_id = data['task_id']
    #     # 获取发送进度
    #     result = self.app.get_msg_send_progress(task_id)
    #     assert result
    #     sleep(5)
    #     result = self.app.get_msg_send_result(task_id=task_id)
    #     assert result
    #     # 测试link消息
    #     data = self.app.async_send_msg(msgtype='link', userid_list=user_ids,
    #                                    msgcontent={
    #                                        "messageUrl": "http://s.dingtalk.com/market/dingtalk/error_code.php",
    #                                        "picUrl": "@lALOACZwe2Rk",
    #                                        "title": "测试",
    #                                        "text": "测试"
    #                                    })
    #     assert data
    #     # 测试发送ActionCard
    #     data = self.app.async_send_msg(msgtype='action_card', userid_list=user_ids,
    #                                    msgcontent={
    #                                        "title": "是透出到会话列表和通知的文案",
    #                                        "markdown": "支持markdown格式的正文内容",
    #                                        "btn_orientation": "1",
    #                                        "btn_json_list": [
    #                                            {
    #                                                "title": "一个按钮",
    #                                                "action_url": "https://www.taobao.com"
    #                                            },
    #                                            {
    #                                                "title": "两个按钮",
    #                                                "action_url": "https://www.tmall.com"
    #                                            }
    #                                        ]
    #                                    })
    #     assert data

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

    # 测试用户操作
    def test_user_operator(self):
        """
        测试创建用户
        为避免在群里频繁出现欢迎信息，通常不测试此方法
        :return:
        """
        assert self.app.access_token
        dept_list = self.app.get_department_list()
        dept_id = None
        for dept in dept_list:
            if dept['name'] == '信息部':
                dept_id = dept['id']
                break
        if dept_id is None:
            dept_id = dept_list[1]['id']
        # 测试创建用户错误
        err_user_info = {
            'name': '马小云',
            'orderInDepts': {dept_id: 8},
            'department': 1234567890,
            'position': '马云，你不认识？？！！',
            'mobile': '13058888882'
        }
        try:
            result = self.app.create_user(**err_user_info)
            assert result
        except BaseException as ex:
            assert '无效的部门JSONArray对象,合法格式需要用中括号括起来,且如果属于多部门,部门id需要用逗号分隔' in str(ex)
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

    # 部门操作相关测试
    def test_dept_operator(self):
        # 获取部门详情
        dept_list = self.app.get_department_list()
        dept_id = dept_list[1]['id']
        resp = self.app.get_department(dept_id)
        assert resp
        # 测试错误的部门id
        try:
            resp = self.app.get_department(123456789)
            assert resp
        except BaseException as ex:
            assert '部门不存在' in str(ex)
        # 测试删除部门
        dept_list = self.app.get_department_list()
        assert dept_list
        for dept in dept_list:
            if '霍格沃茨魔法学校' in dept['name']:
                dept_id = dept['id']
                result = self.app.delete_department(dept_id)
                assert result
        dept_info = {
            'name': '霍格沃茨魔法学校',
            'parentid': 1
        }
        dept_id = self.app.create_department(**dept_info)
        assert dept_id
        # 测试创建部门错误，key错误
        err_dept_info = {
            'dept_name': '霍格沃茨魔法学校',
            'parentid': 1
        }
        try:
            dept_id = self.app.create_department(**err_dept_info)
        except BaseException as ex:
            assert '不合法的部门名称' in str(ex)
        new_dept_info = {
            'id': dept_id,
            'name': '霍格沃茨魔法学校：格兰芬多',
            'parentid': 1
        }
        dept = self.app.update_department(**new_dept_info)
        assert dept
        # 测试更新部门错误
        err_new_dept_info = {
            'id': 1234567890,
            'name': '霍格沃茨魔法学校：格兰芬多',
            'parentid': 1
        }
        try:
            dept = self.app.update_department(**err_new_dept_info)
            assert dept
        except BaseException as ex:
            assert '部门不存在' in str(ex)
        # 测试删除部门
        dept_list = self.app.get_department_list()
        assert dept_list
        for dept in dept_list:
            if '霍格沃茨魔法学校' in dept['name']:
                dept_id = dept['id']
                result = self.app.delete_department(dept_id)
                assert result

    # 获取用户部门
    def test_get_user_depts(self):
        # 获取部门
        dept_list = self.app.get_department_list()
        dept_ids = [dept['id'] for dept in dept_list]
        # 获取用户
        user_list = self.app.get_user_list(dept_ids[1])
        user_id = [user['userid'] for user in user_list][1]
        depts = self.app.get_user_departments(user_id)
        assert depts

    # 获取企业员工数
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
        sign = self.app.jsapi_signature(jsapi_ticket=jsapi_ticket, noncestr=noncestr, timestamp=timestamp, url=url)
        assert sign == '750d0719eeb810f6fa12b04d87d0d7789c4bc64f'

    @staticmethod
    def test_check_callback_signature():
        signature = '5a65ceeef9aab2d149439f82dc191dd6c5cbe2c0'
        timestamp = '1445827045067'
        nonce = 'nEXhMP4r'
        ciphertext = '1a3NBxmCFwkCJvfoQ7WhJHB+iX3qHPsc9JbaDznE1i03peOk1LaOQoRz3+nly' \
                     'GNhwmwJ3vDMG+OzrHMeiZI7gTRWVdUBmfxjZ8Ej23JVYa9VrYeJ5as7XM/ZpulX8' \
                     'NEQis44w53h1qAgnC3PRzM7Zc/D6Ibr0rgUathB6zRHP8PYrfgnNOS9PhSBdHleg' \
                     'K+AGGanfwjXuQ9+0pZcy0w9lQ=='
        token = '123456'
        result = check_callback_signature(token=token, ciphertext=ciphertext,
                                          signature=signature, timestamp=timestamp, nonce=nonce)
        assert result is True

    def test_get_call_back_result(self):
        """
        每次有异常只能调用一次，后续再调用就会返回空列表，直至出现新的异常。
        所以默认情况下不执行此单元测试
        :return:
        """
        assert self.app.access_token
        # self.app.get_call_back_failed_result()

    def test_app_decrypt_encrypt(self):
        plaintext = json.dumps('success')
        ciphertext = self.app.encrypt(plaintext)
        new_plaintext, new_key, new_buf = self.app.decrypt(ciphertext)
        assert plaintext == new_plaintext

    def test_get_all_user_list(self):
        """
        测试获取全公司员工
        :return:
        """
        data = self.app.get_all_users()
        assert data

