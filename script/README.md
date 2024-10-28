# 数据采集

discussions不能通过RESTful API获取

token创建

```
https://github.com/settings/tokens
```

script目录内 `.env`配置

```
GITHUB_USERNAME=
GITHUB_COOKIE=
GITHUB_ACCESS_TOKEN=
MONGODB_IP=
MONGODB_PORT=
MONGODB_USENAME=
MONGODB_PASSWORD=

```

* [X] 使用github自带的搜索进行用户筛选

# 用法

```
cd script
pip install -r requirements.txt
python icehub.py --username SweetIceLolly --output_dir data
```
