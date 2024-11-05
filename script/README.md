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

## Repo 评分策略

核心策略为通过判断某一仓库对于标准仓库的偏离程度（z-score）来进行评分。（权重通过 PCA 无监督获得）

![z-score](assets/equation4158.svg)

1. 影响力
    - star 数量
    - fork 数量
    - watch 数量
    - used by 数量
    - contributor 数量
2. 社区健康度
    - 已解决的 issue 占比
    - issue 的频率（issue 数量比上仓库创建时间，单位为天）

由于时间限制，所有指标的均值和方差通过在 GitHub 上创建的前 1,205,000 个仓库中随机选取的 1000 个仓库进行计算得到。
由于仓库各项数据分布可以看作长尾分布，因此在进一步计算之前应该对所有数据取自然对数处理。最终各项参数如下：

权重：
```json
{"stat":0.77393298, "forks":0.07695682, "watchers":0.05508228, "used_by":0.05038851, "contributors":0.04363072, "last":0.00000868}
```

均值：
```
stars           1.247832
forks           0.502015
watchers        1.247571
used_by         0.073765
contributors    0.061279
last            0.000812
dtype: float64
```

标准差：
```
stars           1.095863
forks           1.013710
watchers        0.664301
used_by         0.410974
contributors    0.453624
last            0.006694
dtype: float64
```

其中 last 为已解决的 issue 占比与 issue 的频率的乘积。

## 用户评分策略

核心策略为通过判断某一用户与其所有交互过的仓库贡献占比来进行评分。共分为三部分：

1. 社区项目参与
2. 个人项目质量与影响力
3. 
