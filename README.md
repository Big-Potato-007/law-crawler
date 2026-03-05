# 法律法规与国家标准爬虫（Python）

一个可扩展的 Python 爬虫项目：用于抓取公开法律法规与国家标准网页（重点支持 `gov.cn`），抽取正文并转换成 Markdown，附带 YAML 头信息后按分类自动保存。

## 功能清单

- ✅ 支持关键词输入（`--keyword`）
- ✅ 支持政府网站检索（内置 `gov.cn` 适配器，可扩展）
- ✅ HTML 正文抽取并转换 Markdown（BeautifulSoup + markdownify）
- ✅ 每个 `.md` 文件包含 YAML front matter
- ✅ 自动分类保存（按 `category/year/source_site`）

## 项目结构

```text
law-crawler/
├── law_crawler/
│   ├── __init__.py
│   ├── cli.py                  # 命令行入口
│   ├── crawler.py              # 通用抓取逻辑 + 重试机制
│   ├── extractor.py            # 正文抽取 + HTML->Markdown + 分类
│   ├── markdown_writer.py      # YAML + Markdown 落盘
│   ├── models.py               # 数据模型
│   └── sources/
│       ├── __init__.py         # 站点注册表
│       └── gov_cn.py           # gov.cn 搜索适配器
├── tests/
├── requirements.txt
├── .gitignore
└── README.md
```

## 安装

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 使用示例

### 1) 关键词检索抓取（gov.cn）

```bash
python -m law_crawler.cli --keyword "食品安全法" --sources gov.cn --max-pages 2 --max-items 20
```

### 2) 直接抓取 URL

```bash
python -m law_crawler.cli \
  --url "https://www.gov.cn/zhengce/2024-01/01/content_xxx.htm" \
  --url "https://www.gov.cn/zhengce/2024-02/02/content_yyy.htm"
```

### 3) 指定输出目录

```bash
python -m law_crawler.cli --keyword "国家标准" --output-dir data_markdown
```

### 4) 控制抓取频率与重试

```bash
python -m law_crawler.cli --keyword "食品安全法" --sleep-seconds 1.2 --retries 3
```

## 输出目录示例

```text
output/
└── regulation/
    └── 2024/
        └── www_gov_cn/
            ├── 国务院关于xxxx通知.md
            └── 市场监管总局关于xxxx公告.md
```

## Markdown 文件示例（YAML 头信息）

```yaml
---
title: 国务院关于xxxx的通知
source_url: https://www.gov.cn/...
source_site: www_gov_cn
category: regulation
published_at: '2024-04-01'
crawled_at: '2026-03-05T08:00:00.000000Z'
keyword: 食品安全法
---

# 正文标题
...
```

## 站点扩展（新增政府网站）

1. 在 `law_crawler/sources/` 新建适配器文件，例如 `miit_gov_cn.py`
2. 实现两个方法：
   - `build_search_url(keyword, page)`
   - `parse_search_links(html)`
3. 在 `law_crawler/sources/__init__.py` 注册到 `SOURCE_REGISTRY`

## 合规说明

- 仅抓取公开页面，需遵守目标站点 robots 与服务条款。
- 建议控制抓取频率（项目默认每次请求后 sleep）。


## 本地验证

```bash
python -m compileall law_crawler tests
python -m unittest discover -s tests -p "test_*.py"
python -m law_crawler.cli --help
```
