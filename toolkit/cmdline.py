#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2017/8/4 上午11:19
# @Author : Matrix
# @Github : https://github.com/blackmatrix7/
# @Blog : http://www.cnblogs.com/blackmatrix/
# @File : cmdline.py
# @Software: PyCharm
import sys
__author__ = 'blackmatrix'


class CmdLine:

    @property
    def config(self):
        args = sys.argv
        return args[1] if len(args) >= 2 else 'default'

    @property
    def command(self):
        args = sys.argv
        return args[2] if len(args) >= 3 else 'runserver'

cmdline = CmdLine()

if __name__ == '__main__':
    pass
