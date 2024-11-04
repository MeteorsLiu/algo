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

## 判断用户地理位置的手段
1. 通过用户的 profile 自述获取地理位置信息
2. 通过用户个人仓库的 README.md 语言分布判断地理位置信息
3. 通过用户双向关注用户的地理位置信息进行推断
4. 通过用户提交 commit 的时区信息进行推断（不准确，同一个时区会对应多个国家）
