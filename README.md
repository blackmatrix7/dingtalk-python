# DingTalk-Python SDK

钉钉第三方SDK，Python版本，用于企业自研微应用。

## 环境

Python3

Redis（或Memcached，或自定义会话管理对象）

## QuickStart

### 安装依赖包

```json
pycrypto==2.6.1
requests==2.18.4
redis==2.10.6
# 或
python3-memcached==1.51
# 或
pymysql==0.8.0
```

在python的环境中执行：

```shell
pip install -r requirements.txt
```

钉钉回调消息的加密解密需要依赖pycrypto。

这个包在Windows下安装比较繁琐，建议在Mac OS或Linux下进行调试。

如果不需要使用钉钉回调消息，则可以不安装pycrypto，不影响其他功能的正常工作。

### 复制模块

将项目的dingtalk模块复制到需要使用的项目根目录下。

暂不考虑将其打包成python的包，主要原因是目前只实现钉钉接口文档的部分功能，如果打包成python包不便于在使用时新增或调整功能。

### 管理钉钉会话

Dingtalk-Python需要依赖缓存服务器对access token、jsapi ticket进行会话过期时间管理，所以需要传入缓存服务器的客户端对象，这里可以选用Redis（推荐）或Memcached。

需要特别注意的是，对于一个企业多个微应用，或一个企业多种环境：如生产环境、测试环境这种情况，务必保证缓存数据的一致，避免频繁调用钉钉jsapi ticket的接口，导致不同缓存服务器的jsapi ticket互相覆盖。

#### 创建Redis对象

```python
import redis
# 使用redis管理钉钉会话
session_manager = redis.Redis(host='127.0.0.1', port='6379', db=0)
```

#### 创建Memcached对象

```python
from memcache import Client
# 使用memcached管理钉钉会话
session_manager = Client(['127.0.0.1:11211'])
```

#### 自定义会话管理对象

除了使用redis和memcached管理钉钉会话外，还支持自定义管理对象，实现对钉钉会话的管理。

通过自定义会话管理对象的方式，可以将钉钉的access token、jsapi ticket存储到MySQL或其它数据库，不仅仅局限于只能使用redis或memcached。

自定义缓存对象需要实现以下类的抽象方法，最后将这个对象实例化后赋值给DingTalkApp的session_manager属性。

```python
class SessionManager:
    """
    钉钉会话管理
    除了支持redis和memcached以外
    也可以通过实现此类的抽象方法支持mysql等数据库
    """

    def set(self, key, value, expires):
        """
        存储会话数据
        :param key: 
        :param value:
        :param expires: 超时时间，单位秒
        :return:
        """
        raise NotImplementedError

    def get(self, key):
        """
        获取会话数据，获取时需要判断会话是否过期
        如已经会话数据已经过期，需要返回None
        :param key:
        :return:
        """
        raise NotImplementedError

    def delete(self, key):
        """
        删除会话数据
        :param key:
        :return:
        """
        raise NotImplementedError
```

### 实例化DingTalk App

```python
from dingtalk import DingTalkApp
# name传入企业名称
# session_manager传入钉钉会话管理对象，如果用缓存服务器进行管理，可以是redis或memcached
# 也可以自行实现一个会话管理的对象
# 用于加解密的aes_key，必须是43位字符串，由大小写字母和数字组成，不能有标点符号
# 如果同个企业需要创建多个app实例时，请保持除agent_id外的参数完全一致
# 以下实例化参数都是模拟数据
app = DingTalkApp(name='test', session_manager=session_manager,
                  agent_id='152919534',
                  corp_id='ding19cdf2s221ef83f635c2e4523eb3418f',
                  corp_secret='3ab8Uk7Wef4ytgf7YZF2EziCAlx6AufdF3dFvfjtu3532FG3AUgWNEJys',
                  aes_key='4g5j64qlyl3zvetqxz5jiocdr586fn2zvjpa8zls3ij')
```

### 调用接口示例

不同的功能分布在app实例不同的子模块中，目前支持以下子模块的部分接口：

| 模块名       | 说明                     |
| --------- | ---------------------- |
| auth      | 钉钉鉴权模块，所有子模块的基础        |
| smartwork | 智能办公模块，含有考勤和流程等接口      |
| contact   | 企业内部通讯录子模块             |
| message   | 企业通知及消息子模块             |
| file      | 文件相关子模块，目前主要用于钉盘       |
| customer  | 外部联系人子模块               |
| callback  | 回调接口子模块，另外还含有加密解密部分的功能 |

直接在app实例中，通过不同的子模块，调用对应的方法即可，不需要传入公共参数部分，公共参数部分会自动补充。

```python
# 获取钉钉后台定义的外部联系人标签
label_groups = app.customer.get_label_groups()
# 获取审批实例
start_time = datetime(year=2017, month=6, day=1, hour=1, minute=1, second=1, microsecond=1)
# 以下皆是模拟数据
data = app.smartwork.get_bpms_instance_list(process_code='PROC-FF6Y4BE1N2-B3OQZGC9RLR4SY1MTNLQ1-91IFWS3', 
                                  start_time=start_time)
```

比较特别是鉴权子模块，既可以通过子模块调用，也可以通过app实例直接调用。

```Python
# 获取access token
app.auth.get_access_token()
# 以下的方法也是等价的
app.get_access_token()
```

同时，提供可以通过钉钉的接口方法名直接调用方法的途径，便于和钉钉的接口文档对应。

```python
# 通过run()方法，传入钉钉的接口方法名，及业务参数(不含公共参数部分)
data = app.run('dingtalk.corp.ext.listlabelgroups', size=20, offset=0)
# 上面的方法等同于
data = app.customer.get_label_groups(size=20, offset=0)
```

这种方式仅限于钉钉本身提供了方法名，一些钉钉本身未提供方法名的情况下，不适用此方法。

如果一定要使用run的形式调用，可以在每个模块的类对象中，以装饰器的形式，给对应的方法加上一个方法名。

```python
@method('dingtalk.corp.ext.all')
def get_all_ext_list(self):
    """
        获取全部的外部联系人
        :return:
        """
    size = 100
    offset = 0
    dd_customer_list = []
    while True:
        dd_customers = self.get_ext_list(size=size, offset=offset)
        if len(dd_customers) <= 0:
            break
            else:
                dd_customer_list.extend(dd_customers)
                offset += size
                return dd_customer_list
```

例如上面的“dingtalk.corp.ext.all”方法，钉钉本身是没有这个方法名的，通过method装饰器，给函数加上一个方法名后，就可以通过`app.run('dingtalk.corp.ext.all')`的方式调用。

## 已实现的接口

等待有空来整理