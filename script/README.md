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

这个接口返回issues和pullrequest

```
https://api.github.com/search/issues?q=involves:MeteorsLiu&per_page=100&page=1
```

# 用法

```
cd script
pip install -r requirements.txt
python icehub.py --help
```
