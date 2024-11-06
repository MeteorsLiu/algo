# 数据采集

discussions不能通过RESTful API获取

token创建

```
https://github.com/settings/tokens
```

`script/.env` 配置

```
GITHUB_USERNAME=
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
   - issue_rate：已解决的 issue 占比 * issue 的频率（issue 数量比上仓库创建时间，单位为天）
   - commit 的频率（commit 数量比上仓库创建时间，单位为天）

由于时间限制，所有指标的均值和方差通过在 GitHub 上创建的前 1,205,000 个仓库中随机选取的 1000 个仓库进行计算得到。
由于仓库各项数据分布可以看作长尾分布，因此在进一步计算之前应该对所有数据取自然对数处理。最终各项参数如下：

均值：

```
stars           1.132366
forks           0.451522
watchers        1.199872
used_by         0.101942
contributors    1.192904
commit_rate     0.159262
issue_rate      0.000105
dtype: float64
```

标准差：

```
stars           0.990616
forks           0.844213
watchers        0.571998
used_by         0.684791
contributors    1.407939
commit_rate     0.460403
issue_rate      0.002566
dtype: float64
```

同时通过处理 PCA 载荷信息，取一组如下权重：

```json
{
   "stars": 0.229479,
   "forks": 0.227530,
   "watchers": 0.104085,
   "used_by": 0.102685,
   "contributors": 0.913740,
   "issue_rate": 0.198170,
   "commit_rate": 0.000304
}
```

（可以看到其中 contributors 项对该 PC 的贡献最大且全为正数，符合贡献者越多的仓库越可能是优质仓库的直觉）

## 用户评分策略

核心策略为通过判断某一用户与其所有交互过的仓库贡献占比来进行评分。共分为三部分：

1. 社区项目参与
2. 个人项目质量与影响力
3. 

## 后端启动

```
cd script
flask --app api.py run --host=0.0.0.0 --port=7000 --debug
```
