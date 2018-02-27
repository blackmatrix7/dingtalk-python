#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2018/2/27 上午11:42
# @Author : Matrix
# @Github : https://github.com/blackmatrix7/
# @Blog : http://www.cnblogs.com/blackmatrix/
# @File : __init__.py
# @Software: PyCharm
from flask import Flask
from decimal import Decimal
from datetime import datetime
from flask.json import JSONEncoder

__author__ = 'blackmatrix'


class CustomJSONEncoder(JSONEncoder):

    datetime_format = None

    def default(self, obj):
        try:
            if isinstance(obj, datetime):
                return obj.strftime(CustomJSONEncoder.datetime_format)
            elif isinstance(obj, Decimal):
                # 不转换为float是为了防止精度丢失
                return str(obj)
            iterable = iter(obj)
        except TypeError:
            pass
        else:
            return list(iterable)
        return JSONEncoder.default(self, obj)


def register_blueprints(app):
    """
    注册蓝本
    :param app:
    :return:
    """
    pass


def register_extensions(app):
    """
    注册扩展
    :param app:
    :return:
    """
    pass


def create_app(app_config, datetime_format='%Y-%m-%d %H:%M:%S'):
    """
    Flask 工厂函数
    :return:
    """

    app = Flask(__name__)
    # 读取配置
    app.config.from_object(app_config)

    # 注册蓝本与扩展
    register_blueprints(app)
    register_extensions(app)

    # 自定义JSON的日期格式
    CustomJSONEncoder.datetime_format = datetime_format
    app.json_encoder = CustomJSONEncoder

    return app

if __name__ == '__main__':
    pass
