script目录内 `.env`配置

```
GITHUB_COOKIE=
```

* [X] 使用github自带的搜索进行用户筛选

# 用法

```
cd script
pip install -r requirements.txt
python icehub.py --username SweetIceLolly --output_dir data
```

## 判断用户地理位置的手段

1. 通过用户的 profile 自述获取地理位置信息
2. 通过用户个人仓库的 README.md 语言分布判断地理位置信息
3. 通过用户双向关注用户的地理位置信息进行推断
4. 通过用户提交 commit 的时区信息进行推断（不准确，同一个时区会对应多个国家）

## Repo 评分策略

核心策略为通过判断某一仓库对于标准仓库的偏离程度（z-score）来进行评分。（权重通过）

1. 影响力（logarithm）
    - star 数量
    - fork 数量
    - watch 数量
    - used by 数量
    - 第三方包管理器数据
2. 社区健康度
    - 已解决的 issue 占比
    - issue 的频率

首先需要爬取大量随机仓库的数据，并对所有的数据取对数来抑制极端值，因为 GitHub 上的仓库数量分布是一个长尾分布。

## 用户评分策略

核心策略为通过判断某一用户与其所有交互过的仓库贡献占比来进行评分。
