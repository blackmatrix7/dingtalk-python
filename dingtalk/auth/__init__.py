#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time: 2018/2/28 下午3:12
# @Author: BlackMatrix
# @Site: https://github.com/blackmatrix7
# @File: __init__.py
# @Software: PyCharm
import logging
from .token import *
from .ticket import *
from time import sleep
from functools import partial
from ..foundation import dingtalk_method

__author__ = 'blackmatrix'

METHODS = {}

method = partial(dingtalk_method, methods=METHODS)


class Auth:

    def __init__(self, name, session_manager, corp_id, corp_secret):
        self.name = name
        self.corp_id = corp_id
        self.corp_secret = corp_secret
        self.session_manager = session_manager
        self.methods = METHODS

    def get_access_token(self):
        """
        在缓存中设置access token 7000秒过期，每次过期会自动重新获取 access token
        :return:
        """
        access_token = None
        access_token_key = '{}_access_token'.format(self.name)
        logging.info('准备获取access token， access token key：{}'.format(access_token_key))
        try:
            if self.session_manager.get(access_token_key) is not None:
                access_token = self.session_manager.get(access_token_key)
                # 兼容redis
                try:
                    access_token = access_token.decode()
                except AttributeError:
                    pass
                logging.info('命中缓存{0}，直接返回缓存数据：{1}'.format(access_token_key, access_token))
            else:
                logging.warning('没有命中缓存{0}，准备重新向钉钉请求access token'.format(access_token_key))
                logging.info('先行清理缓存中的jsapi ticket数据')
                self.session_manager.delete('{}_jsapi_ticket'.format(self.name))
                time_out = 7000
                access_token = self.refresh_access_token(time_out)
        except BaseException as ex:
            logging.error('获取access token异常：{}'.format(ex))
        finally:
            return access_token

    @property
    def access_token(self):
        return self.get_access_token()

    def refresh_access_token(self, time_out=7000):
        """
        刷新access_token
        :return:
        """
        access_token_key = '{}_access_token'.format(self.name)
        self.session_manager.delete(access_token_key)
        logging.info('已清理access token相关缓存'.format(access_token_key))
        resp = get_access_token(self.corp_id, self.corp_secret)
        access_token = resp['access_token']
        logging.info('已重新向钉钉请求access token：{1}'.format(access_token_key, access_token))
        self.session_manager.set(access_token_key, access_token, time_out)
        logging.info('将{0}: {1} 写入缓存，过期时间{2}秒'.format(access_token_key, access_token, time_out))
        return access_token

    def get_jsapi_ticket(self):
        """
        获取当前缓存中的jsapi ticket
        如果没有命中缓存，则强制刷新jsticket
        :return:
        """
        jsapi_ticket_key = '{}_jsapi_ticket'.format(self.name)
        ticket_lock_key = '{}_ticket_lock'.format(self.name)

        def _get_jsapi_ticket():
            if self.session_manager.get(jsapi_ticket_key) is not None:
                jaspi_ticket = self.session_manager.get(jsapi_ticket_key)
                # 兼容redis
                try:
                    jaspi_ticket = jaspi_ticket.decode()
                except AttributeError:
                    pass
                logging.info('命中缓存{}，直接返回缓存数据：{}'.format(jsapi_ticket_key, jaspi_ticket))
            else:
                logging.warning('没有命中缓存{}，准备重新向钉钉请求 jsapi ticket'.format(jsapi_ticket_key))
                # jsapi ticket 过期时间，单位秒
                time_out = 3600
                # 获取jsapi ticket的锁
                ticket_lock = self.session_manager.get(ticket_lock_key)
                if ticket_lock and (ticket_lock is True or str(ticket_lock).lower() == 'true'):
                    logging.warning('jsapi ticket 存在锁，等待其他调用者请求新的 jsapi ticket')
                    sleep(0.5)
                    jaspi_ticket = _get_jsapi_ticket()
                else:
                    logging.info('jsapi ticket 未加锁，可以请求新的 jsapi ticket')
                    jaspi_ticket = self.refresh_jsapi_ticket(time_out)
            return jaspi_ticket

        jsapi_ticket = _get_jsapi_ticket()
        return jsapi_ticket

    @property
    def jsapi_ticket(self):
        return self.get_jsapi_ticket()

    def refresh_jsapi_ticket(self, time_out=3600):
        """
        强制刷新 jsapi ticket
        :param time_out:
        :return:
        """
        jsapi_ticket_key = '{}_jsapi_ticket'.format(self.name)
        ticket_lock_key = '{}_ticket_lock'.format(self.name)
        jaspi_ticket = None
        try:
            # 为jsapi ticket加锁
            self.session_manager.set(ticket_lock_key, True, 60)
            logging.info('已为jsapi ticket加锁，防止重复请求新的 jsapi ticket')
            # 主动清理之前的jsapi ticket缓存
            self.session_manager.delete(jsapi_ticket_key)
            # 检查是否清理成功
            assert self.session_manager.get(jsapi_ticket_key) is None
            # 请求新的jsapi ticket
            resp = get_jsapi_ticket(self.access_token)
            jaspi_ticket = resp['ticket']
            logging.info('已向钉钉请求新的jsapi ticket：{}'.format(jaspi_ticket))
            # 将新的jsapi ticket写入缓存
            self.session_manager.set(jsapi_ticket_key, jaspi_ticket, time_out)
            logging.info('将jsapi ticket写入缓存{}：{}，过期时间{}秒'.format(jsapi_ticket_key, jaspi_ticket, time_out))
        except Exception as ex:
            # 出现异常时，清理全部jsapi ticket的相关缓存数据
            self.session_manager.delete(jsapi_ticket_key)
            logging.error('强制刷新jsapi ticket出现异常，清理jsapi ticket缓存。异常信息：{}'.format(str(ex)))
        finally:
            # 解除jsapi ticket的锁
            logging.info('解除jsapi ticket的锁{}，其他调用者可以请求新的jsapi ticket'.format(ticket_lock_key))
            self.session_manager.delete(ticket_lock_key)
            return jaspi_ticket

    @staticmethod
    def jsapi_signature(jsapi_ticket, noncestr, timestamp, url):
        """
        计算签名信息
        :param jsapi_ticket:
        :param noncestr:
        :param timestamp:
        :param url:
        :return:
        """
        logging.info('jsapi_ticket:{}'.format(jsapi_ticket))
        logging.info('noncestr:{}'.format(noncestr))
        logging.info('timestamp:{}'.format(timestamp))
        logging.info('url:{}'.format(url))
        sign = generate_jsapi_signature(jsapi_ticket=jsapi_ticket, noncestr=noncestr, timestamp=timestamp, url=url)
        logging.info('sign:{}'.format(sign))
        return sign

if __name__ == '__main__':
    pass
