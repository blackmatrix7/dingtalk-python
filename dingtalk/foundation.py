#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2017/11/30 下午2:35
# @Author : Matrix
# @Github : https://github.com/blackmatrix7/
# @Blog : http://www.cnblogs.com/blackmatrix/
# @File : methods.py
# @Software: PyCharm
import time
import requests
from .configs import *
from functools import wraps
from datetime import datetime
from .exceptions import DingTalkExceptions

__author__ = 'blackmatrix'


class StopRetry(Exception):

    def __repr__(self):
        return 'retry stop'


def retry(max_retries: int =5, delay: (int, float) =0, step: (int, float) =0,
          exceptions: (BaseException, tuple, list) =BaseException,
          sleep=time.sleep, callback=None, validate=None):
    """
    函数执行出现异常时自动重试的简单装饰器。
    :param max_retries:  最多重试次数。
    :param delay:  每次重试的延迟，单位秒。
    :param step:  每次重试后延迟递增，单位秒。
    :param exceptions:  触发重试的异常类型，单个异常直接传入异常类型，多个异常以tuple或list传入。
    :param sleep:  实现延迟的方法，默认为time.sleep。
    在一些异步框架，如tornado中，使用time.sleep会导致阻塞，可以传入自定义的方法来实现延迟。
    自定义方法函数签名应与time.sleep相同，接收一个参数，为延迟执行的时间。
    :param callback: 回调函数，函数签名应接收一个参数，每次出现异常时，会将异常对象传入。
    可用于记录异常日志，中断重试等。
    如回调函数正常执行，并返回True，则表示告知重试装饰器异常已经处理，重试装饰器终止重试，并且不会抛出任何异常。
    如回调函数正常执行，没有返回值或返回除True以外的结果，则继续重试。
    如回调函数抛出异常，则终止重试，并将回调函数的异常抛出。
    :param validate: 验证函数，用于验证执行结果，并确认是否继续重试。
    函数签名应接收一个参数，每次被装饰的函数完成且未抛出任何异常时，调用验证函数，将执行的结果传入。
    如验证函数正常执行，且返回False，则继续重试，即使被装饰的函数完成且未抛出任何异常。
    如回调函数正常执行，没有返回值或返回除False以外的结果，则终止重试，并将函数执行结果返回。
    如验证函数抛出异常，且异常属于被重试装饰器捕获的类型，则继续重试。
    如验证函数抛出异常，且异常不属于被重试装饰器捕获的类型，则将验证函数的异常抛出。
    :return: 被装饰函数的执行结果。
    """
    def wrapper(func):
        @wraps(func)
        def _wrapper(*args, **kwargs):
            nonlocal delay, step, max_retries
            func_ex = StopRetry
            while max_retries > 0:
                try:
                    result = func(*args, **kwargs)
                    # 验证函数返回False时，表示告知装饰器验证不通过，继续重试
                    if callable(validate) and validate(result) is False:
                        continue
                    else:
                        return result
                except exceptions as ex:
                    func_ex = ex
                    # 回调函数返回True时，表示告知装饰器异常已经处理，终止重试
                    if callable(callback) and callback(ex) is True:
                        return
                finally:
                    max_retries -= 1
                    if delay > 0 or step > 0:
                        sleep(delay)
                        delay += step
            else:
                raise func_ex
        return _wrapper
    return wrapper


def get_timestamp():
    """
    生成时间戳
    :return:
    """

    now = datetime.now()
    timestamp = datetime.timestamp(now)
    timestamp = int(round(timestamp))
    return timestamp


def get_request_url(access_token, method=None, format_='json', v='2.0', simplify='false', partner_id=None, url=None):
    """
    通用的获取请求地址的方法
    :param access_token:
    :param method:
    :param format_:
    :param v:
    :param simplify:
    :param partner_id:
    :param url:
    :return:
    """
    from datetime import datetime
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    base_url = url or DING_METHODS_URL
    request_url = '{0}?method={1}&session={2}&timestamp={3}&format={4}&v={5}'.format(base_url, method, access_token,
                                                                                     timestamp, format_, v)
    if format_ == 'json':
        request_url = '{0}&simplify={1}'.format(request_url, simplify)
    if partner_id:
        request_url = '{0}&partner_id={1}'.format(request_url, partner_id)
    return request_url


def dingtalk_unpack_result(result):
    """
    统一钉钉的返回格式
    :param result:
    :return:
    """
    try:
        for k1, v1 in result.items():
            for k2, v2 in v1.items():
                if k2 == 'result' and isinstance(v2, dict):
                    return v2
            else:
                return result
        else:
            return result
    except AttributeError:
        return result


def dingtalk_resp(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        resp = func(*args, **kwargs)
        data = resp.json()
        if resp.status_code == 200:
            # 针对钉钉几种有明确返回错误信息的情况进行处理
            if 'errcode' in data and data['errcode'] != 0:
                raise DingTalkExceptions.dingtalk_resp_err(http_code=resp.status_code,
                                                           err_code=data['errcode'],
                                                           err_msg=data.get('errmsg') or data['errcode'])
            elif 'error_response' in data and data['error_response']['code'] != 0:
                request_id = data['error_response']['request_id']
                err_code = data['error_response'].get('sub_code') or data['error_response']['code']
                err_msg = data['error_response'].get('sub_msg') or data['error_response']['msg']
                raise DingTalkExceptions.dingtalk_resp_err(http_code=resp.status_code,
                                                           err_code=err_code,
                                                           err_msg='{}(request_id:{})'.format(err_msg, request_id))
            else:
                # 对于一些返回格式不统一的接口，需要对返回的数据做拆解，再判断是否存在异常
                result = dingtalk_unpack_result(data)
                if result.get('is_success', True) is False or result.get('success', True) is False:
                    if 'error_response' in result:
                        err_code = result['error_response'].get('ding_open_errcode')
                        err_msg = result['error_response'].get('err_msg')
                    else:
                        err_code = result.get('ding_open_errcode')
                        err_msg = result.get('error_msg')
                    raise DingTalkExceptions.dingtalk_resp_err(http_code=resp.status_code, err_code=err_code, err_msg=err_msg)
                # 其他暂时无法明确返回错误的，直接返回接口调用结果
                else:
                    return data
        else:
            raise DingTalkExceptions.dingtalk_resp_err(http_code=resp.status_code,
                                                       err_code=data['errcode'],
                                                       err_msg=data['errmsg'])
    return wrapper


def call_dingtalk_webapi(access_token, method_name, http_method='POST', **kwargs):
    url = get_request_url(access_token, method_name)
    if http_method.upper() == 'POST':
        resp = requests.post(url, data=kwargs)
    else:
        resp = requests.get(url, params=kwargs)
    return resp
