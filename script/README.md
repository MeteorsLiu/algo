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

## 判断用户地理位置的函数设计

1. **用户 Profile 自述信息**：通过 OSM 的地理位置信息反查 API 查询用户 Github Profile 的 `location` 字段尝试获得地理位置的正式描述，例如
   `UC, Berkeley` 将会返回 `Berkeley, California, United States`。
    - 若成功获得则将国家信息与置信概率为 `1` 作为返回值。
    - 若没有匹配的结果（例如用户 `location` 字段为 `uwu`）则返回 `None`。

2. **用户个人仓库 README.md 语言分布**：通过获取用户个人仓库的 README.md 全文，使用 `langdetect` 库判断用户的语言分布，例如
   `[('en', 0.99), ('zh-cn', 0.01)]`。
    - 由于英文的特殊性质，英文为主要语言时将被视为无效项。
    - 在获取到所有有效项后，将会对所有出现的语言概率取平均，得到用户可能的语言分布。
    - 若可能性最大的语言置信概率仍然较低，则返回 `None`。
    - 若置信概率较高，则将语言信息进行查表，得到国家信息与置信概率为作为最终返回值。

3. **双向关注用户推断**：通过获取用户的双向关注用户列表，对所有用户进行上述两种方法的推断，并将所有推断结果进行统计，最终返回出现次数最多的国家信息与置信概率。

4. **用户提交 commit 的时区信息**：该方法不准确，因为同一个时区会对应多个国家。仅会在上述方法均失效时采用。

每一种方法在失败后都会向下采用下一种方法，来保证尽可能多的用户地理位置信息。

## 用户评分策略

核心策略分为三步：

1. **获取用户所有有过交互的仓库**：包括 issue 和 pull request。
2. **通过仓库数据计算仓库评分**
3. **通过用户参与度与仓库评分计算用户评分**：用户参与度考虑了：用户参与的 issue 数与用户参与的 pull request 数。

对于仓库分数，本项目通过判断某一仓库对于标准仓库的偏离程度（z-score）来进行评分。（权重通过 PCA 无监督获得）

![z-score](assets/equation4158.svg)

1. 影响力
    - star 数量
    - fork 数量
    - watch 数量
    - subscribers 数量
2. 社区健康度
    - issues：issue 的数量
    - prs：pull request 的数量

由于时间限制，所有指标的均值和方差通过在 GitHub 上创建的前 1,205,000 个仓库中随机选取的 100,000 个仓库进行计算得到。
由于仓库各项数据分布可以看作长尾分布，因此在进一步计算之前应该对所有数据取自然对数处理。最终各项参数如下：

均值：

```json
{
  "stars": 4.160266,
  "forks": 2.989522,
  "watches": 4.160266,
  "subscribers": 2.329286,
  "issues": 0.842846,
  "prs": 0.652200
}
```

标准差：

```json
{
  "stars": 2.752807,
  "forks": 2.206446,
  "watches": 2.752807,
  "subscribers": 1.417005,
  "issues": 0.945928,
  "prs": 0.893581
}
```

同时通过处理 PCA 载荷信息，取一组如下权重：

```json
{
  "stars": 0.594451,
  "forks": 0.4606115,
  "watches": 0.594451,
  "subscribers": 0.2720080,
  "issues": 0.08193683,
  "prs": 0.01975785
}
```

（可以看到其中 stars 和 watches 项对该主成分的贡献最大且全为正数，符合获 star 和关注越多的仓库越可能是优质仓库的直觉）。

## 后端启动

```
cd script
flask --app api.py run --host=0.0.0.0 --port=7000 --debug
```
