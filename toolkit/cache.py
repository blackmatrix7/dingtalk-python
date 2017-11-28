#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time: 2017/7/9 下午1:28
# @Author: BlackMatrix
# @Site: https://github.com/blackmatrix7
# @File: cache.py
# @Software: PyCharm
import pickle
import hashlib
from memcache import Client
from functools import wraps
from inspect import signature
from collections import OrderedDict

__author__ = 'blackmatrix'

SERVER_MAX_KEY_LENGTH = 250
SERVER_MAX_VALUE_LENGTH = 1024*1024
_DEAD_RETRY = 30
_SOCKET_TIMEOUT = 3


class Cache(Client):

    """
    基于Python3-Memcached客户端轻度封装的缓存操作类
    """

    def __init__(self, *, decorator_enable=True, config=None, servers: list = None, key_prefix: str= '',
                 debug=False, pickle_protocol=0, pickler=pickle.Pickler, unpickler=pickle.Unpickler,
                 pload=None, pid=None, server_max_key_length=SERVER_MAX_KEY_LENGTH,
                 server_max_value_length=SERVER_MAX_VALUE_LENGTH, dead_retry=_DEAD_RETRY,
                 socket_timeout=_SOCKET_TIMEOUT, cache_cas=False, flush_on_reconnect=0,
                 check_keys=True):
        """
        初始化Memcached客户端
        :param decorator_enable:  是否启用缓存，如果为False，缓存装饰器不会生效，主要解决在某些开发环境下不希望应用缓存的问题。
        :param config:  配置文件，dict，详细的配置文件项目说明见后。
                                当配置文件项目与__init__参数重复时，以配置文件项目为准。
        :param servers:  Memcached 服务器列表
        :param key_prefix:  key 前缀，会在每个key中加入对应的字符串前缀。
        :param debug:
        :param pickle_protocol:
        :param pickler:
        :param unpickler:
        :param pload:
        :param pid:
        :param server_max_key_length:
        :param server_max_value_length:
        :param dead_retry:
        :param socket_timeout:
        :param cache_cas:
        :param flush_on_reconnect:
        :param check_keys:

        目前在配置文件中支持如下参数：
        DEBUG： 是否启动debug模式
        CACHE_KEY_PREFIX： key 前缀，会在每个key中加入对应的字符串前缀。
            举个栗子：
            初始化时使用前缀 test，那么在后续调用set等方法设置缓存时，传入的
            key会自动加入这个前缀。
            set(key=''hello, value='value')，实际上在memcached中的key是testhello。
        CACHE_MEMCACHED_SERVERS： memcached服务器列表
        CACHE_DECORATOR_ENABLE: cached缓存装饰器是否生效，此配置主要解决开发环境下不希望缓存生效的情况。
        """
        config = config or {}
        self.debug = config.get('DEBUG', debug)
        self.key_prefix = config.get('CACHE_KEY_PREFIX', key_prefix)
        self.servers = config.get('CACHE_MEMCACHED_SERVERS', servers)
        self.caching = config.get('CACHE_DECORATOR_ENABLE', decorator_enable)

        super().__init__(servers=self.servers, debug=self.debug, pickleProtocol=pickle_protocol,
                         pickler=pickler, unpickler=unpickler, pload=pload, pid=pid,
                         server_max_key_length=server_max_key_length,
                         server_max_value_length=server_max_value_length, dead_retry=dead_retry,
                         socket_timeout=socket_timeout, cache_cas=cache_cas,
                         flush_on_reconnect=flush_on_reconnect, check_keys=check_keys)

    def get(self, key):
        key = '{0}{1}'.format(self.key_prefix, key)
        return super().get(key)

    def set(self, key, val, time=0, min_compress_len=0):
        key = '{0}{1}'.format(self.key_prefix, key)
        super().set(key, val, time, min_compress_len)

    def delete(self, key, time=0):
        key = '{0}{1}'.format(self.key_prefix, key)
        super().delete(key, time)

    def incr(self, key, delta=1):
        key = '{0}{1}'.format(self.key_prefix, key)
        return super().incr(key=key, delta=delta)

    def decr(self, key, delta=1):
        key = '{0}{1}'.format(self.key_prefix, key)
        return super().decr(key=key, delta=delta)

    def add(self, key, val, time=0, min_compress_len=0):
        key = '{0}{1}'.format(self.key_prefix, key)
        return super().add(key=key, val=val, time=time, min_compress_len=min_compress_len)

    def append(self, key, val, time=0, min_compress_len=0):
        key = '{0}{1}'.format(self.key_prefix, key)
        return super().append(key=key, val=val, time=time, min_compress_len=min_compress_len)

    def prepend(self, key, val, time=0, min_compress_len=0):
        key = '{0}{1}'.format(self.key_prefix, key)
        return super().prepend(key=key, val=val, time=time, min_compress_len=min_compress_len)

    def replace(self, key, val, time=0, min_compress_len=0):
        key = '{0}{1}'.format(self.key_prefix, key)
        return super().replace(key=key, val=val, time=time, min_compress_len=min_compress_len)

    def cas(self, key, val, time=0, min_compress_len=0):
        key = '{0}{1}'.format(self.key_prefix, key)
        return super().cas(key=key, val=val, time=time, min_compress_len=min_compress_len)

    def set_multi(self, mapping, time=0, key_prefix='', min_compress_len=0):
        return super().set_multi(mapping=mapping, time=time, key_prefix=key_prefix, min_compress_len=min_compress_len)

    def gets(self, key):
        key = '{0}{1}'.format(self.key_prefix, key)
        return super().gets(key)

    def get_multi(self, keys, key_prefix=''):
        keys = ['{0}{1}'.format(self.key_prefix, key) for key in keys]
        return super().get_multi(keys, key_prefix=key_prefix)

    def delete_multi(self, keys, time=0, key_prefix=''):
        keys = ['{0}{1}'.format(self.key_prefix, key) for key in keys]
        return super().delete_multi(keys=keys, time=time, key_prefix=key_prefix)

    def check_key(self, key, key_extra_len=0):
        key = '{0}{1}'.format(self.key_prefix, key)
        return super().check_key(key=key, key_extra_len=key_extra_len)

    @staticmethod
    def _create_args_sig(func, *args,  **kwargs):
        args_sig = None
        try:
            # 函数名称
            func_name = func.__name__ if callable(func) else func
            params = signature(func).parameters
            args_count = len(args)
            # 复制一份函数参数列表，避免对外部数据的修改
            args = list(args)
            # 将 POSITIONAL_OR_KEYWORD 的参数转换成 k/w 的形式
            if args:
                for index, (key, value) in enumerate(params.items()):
                    if str(value.kind) == 'POSITIONAL_OR_KEYWORD':
                        if index < args_count:
                            kwargs.update({key: args.pop(0)})
            # 对参数进行排序
            args.extend(({k: kwargs[k]} for k in sorted(kwargs.keys())))
            # 将函数参数转换为签名
            func_args = '{0}{1}'.format(func_name, pickle.dumps(args))
            args_sig = hashlib.sha256(func_args.encode()).hexdigest()
        finally:
            # 如果生成参数签名过程中出现异常，则返回None
            return args_sig

    def cached(self, key, timeout=36000, maxsize=30):
        """
        函数装饰器，装饰到函数上时，会优先返回缓存的值。
        :param key: memcached key
        :param timeout: 超时时间，单位秒
        :param maxsize: 最多缓存的数量，因为每次不同参数的函数调用都会生成对应的缓存，控制数量避免占用过多内存
        :return:
        """
        def _cached(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                # 从缓存里获取数据
                func_cache = self.get(key) or OrderedDict()
                # 生成函数参数签名
                args_sig = self._create_args_sig(func, *args, **kwargs)
                if self.caching is False or args_sig is None:
                    result = func(*args, **kwargs)
                else:
                    # 将签名作为key，读取缓存中的函数执行结果
                    result = func_cache.get(args_sig)
                    if result is None:
                        result = func_cache.get(args_sig, func(*args, **kwargs))
                    # 如果签名未被缓存，且缓存数量超出限制大小则删除最早的缓存
                    if len(func_cache) >= maxsize and args_sig not in func_cache:
                        func_cache.popitem(last=False)
                    if args_sig in func_cache:
                        func_cache.move_to_end(args_sig)
                    # 更新缓存结果
                    func_cache.update({args_sig: result})
                    self.set(key=key, val=func_cache, time=timeout)
                return result
            return wrapper
        return _cached

    def delcache(self, key):
        """
        清理缓存装饰器，装饰到函数上时，每次函数执行完毕会清理对应的缓存
        :param key:
        :return:
        """
        def _delcache(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                try:
                    result = func(*args, **kwargs)
                    return result
                except Exception as ex:
                    raise ex
                finally:
                    self.delete(key)
            return wrapper
        return _delcache


if __name__ == '__main__':
    pass



