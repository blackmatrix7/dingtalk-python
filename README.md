# Dingtalk-Python SDK

钉钉第三方SDK，Python版本，用于企业自研微应用。

## 环境

python3

memcached

## QuickStart

### 安装依赖包

```json
certifi==2017.11.5
chardet==3.0.4
idna==2.6
pycrypto==2.6.1
python3-memcached==1.51
requests==2.18.4
six==1.11.0
urllib3==1.22
```

在python的环境中执行：

```shell
pip install -r requirements.txt
```

### 创建memcached对象

Dingtalk-Python需要依赖memcahed对access token，jsticket进行过期时间管理，所以需要python3-memcached所实例化出的对象。

```python
from memcache import Client
# 缓存
cache = Client([127.0.0.1:11211])
```

### 实例化DingTalk App

```python
from dingtalk import DingTalkApp
# 模拟数据
# name传入企业名称，同个企业需要创建多个app实例时，请保持name的值一致
# cache传入python3-memeched的Client类实例化出的对象
# 用于加解密的aes_key，必须是43为字符串，由大小写字母和数字组成，不能有标点符号
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

