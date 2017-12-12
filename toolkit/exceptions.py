#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2017/11/28 下午5:06
# @Author : Matrix
# @Github : https://github.com/blackmatrix7/
# @Blog : http://www.cnblogs.com/blackmatrix/
# @File : exceptions.py
# @Software: PyCharm
import types

__author__ = 'blackmatrix'

_no_value = object()


class SysException(BaseException):

    """
    以描述符进行异常管理：
    禁止对已经设定的异常信息进行修改
    读取异常信息时，每次实例化一个全新的异常实例，避免对异常信息的修改影响全局
    """

    def __init__(self, err_code, err_msg, http_code=500, err_type=BaseException):
        self.err_msg = err_msg
        self.err_type = err_type
        self.err_code = err_code
        self.http_code = http_code

    def __set__(self, instance, value):
        raise AttributeError('禁止修改异常设定')

    def __get__(self, instance, owner):
        supers = (SysException, self.err_type, BaseException) \
            if self.err_type and self.err_type is not BaseException else (SysException, BaseException)
        api_ex_cls = types.new_class('SysException', supers, {}, lambda ns: ns)
        api_ex = api_ex_cls(err_msg=self.err_msg, err_code=self.err_code, http_code=self.http_code)
        return api_ex

    def __str__(self):
        return '异常编号：{err_code} 异常信息：{err_msg}'.format(
            err_code=self.err_code,
            err_msg=self.err_msg)

    # 让类实例变成可调用对象，用于接收自定义异常信息，并抛出
    def __call__(self, err_msg=_no_value, *, err_code=_no_value, http_code=_no_value):
        if err_msg is not _no_value:
            self.err_msg = '{0}，{1}'.format(self.err_msg, err_msg)
        if err_code is not _no_value:
            self.err_code = err_code
        if http_code is not _no_value:
            self.http_code = http_code
        return self


if __name__ == '__main__':
    pass
