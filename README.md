# Dingtalk-Python SDK

钉钉第三方SDK，Python版本，用于企业自研微应用。

## 环境

Python3

Redis（或Memcached）

## QuickStart

### 安装依赖包

```json
pycrypto==2.6.1
redis==2.10.6
# 或
python3-memcached==1.51
requests==2.18.4
```

在python的环境中执行：

```shell
pip install -r requirements.txt
```

钉钉回调消息的加密解密需要依赖pycrypto。

这个包在Windows下安装比较繁琐，建议在Mac OS或Linux下进行调试。

如果不需要使用钉钉回调消息，则可以不安装pycrypto，不影响其他功能的正常工作。

Dingtalk-Python需要依赖缓存服务器对access token、jsticket进行过期时间管理，所以需要传入缓存服务器的客户端，这里可以选用Redis（推荐）或Memcached。

需要特别注意的是，对于一个企业多个微应用，或一个企业多种环境：如生产环境、测试环境这种情况，务必保证缓存数据的一致，避免频繁调用钉钉jsticket的接口，导致不同缓存服务器的jsticket互相覆盖。

### 创建Redis对象

```python
import redis
# 缓存，Redis支持
cache = redis.Redis(host='127.0.0.1', port='6379', db=0)
```

### 创建Memcached对象

```python
from memcache import Client
# memcached客户端
cache = Client(['127.0.0.1:11211'])
```

### 实例化DingTalk App

```python
from dingtalk import DingTalkApp
# name传入企业名称
# cache传入缓存服务器的客户端实例，可以是Redis或Memcached
# 用于加解密的aes_key，必须是43位字符串，由大小写字母和数字组成，不能有标点符号
# 如果同个企业需要创建多个app实例时，请保持除agent_id外的参数完全一致
# 以下实例化参数都是模拟数据
app = DingTalkApp(name='test', cache=cache,
                  agent_id='152919534',
                  corp_id='ding19cdf2s221ef83f635c2e4523eb3418f',
                  corp_secret='3ab8Uk7Wef4ytgf7YZF2EziCAlx6AufdF3dFvfjtu3532FG3AUgWNEJys',
                  aes_key='4g5j64qlyl3zvetqxz5jiocdr586fn2zvjpa8zls3ij')
```

### 调用接口示例

直接在app实例中，调用对应的方法即可，不需要传入公共参数部分，公共参数部分会自动补充。

```python
# 获取钉钉后台定义的外部联系人标签
label_groups = app.get_label_groups()
# 获取审批实例
start_time = datetime(year=2017, month=6, day=1, hour=1, minute=1, second=1, microsecond=1)
# 以下皆是模拟数据
data = app.get_bpms_instance_list(process_code='PROC-FF6Y4BE1N2-B3OQZGC9RLR4SY1MTNLQ1-91IFWS3', 
                                  start_time=start_time)
```

同时，提供可以通过钉钉的接口方法名直接调用方法的途径，便于和钉钉的接口文档对应。

```python
# 通过run()方法，传入钉钉的接口方法名，及业务参数(不含公共参数部分)
data = app.run('dingtalk.corp.ext.listlabelgroups', size=20, offset=0)
# 上面的方法等同于
data = app.get_label_groups(size=20, offset=0)
```

这种方式仅限于钉钉本身提供了方法名，一些钉钉本身未提供方法名的情况下，不适用此方法。如果一定要使用run的形式调用，可以在`dingtalk/__init__.py`的实现中，以装饰器的形式，给对应的方法加上一个方法名。

```python
@dingtalk('dingtalk.corp.ext.list')
def get_ext_list(self, size=20, offset=0):
    """
    获取外部联系人
    :return:
    """
    resp = get_corp_ext_list(self.access_token, size=size, offset=offset)
    result = json.loads(resp['dingtalk_corp_ext_list_response']['result'])
    return result
```

