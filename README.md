# law-crawler（第一阶段：中央法规 / 中央通知批量采集原型）

本项目在现有架构上持续优化，当前阶段聚焦：

- **中央法律 / 行政法规 / 部门规章**（统一输出到 `output/regulations/`）
- **国务院及中央部委通知/公告/意见/办法/细则/指南等政策文件**（统一输出到 `output/notices/`）

> 暂不覆盖：国家/行业/地方标准、地方法规/通知、新增站点、AI 解读、PDF 复杂解析。

## 已有能力

- CLI 入口：`python -m law_crawler.cli`
- 支持关键词检索（`gov.cn`）与 URL 直抓
- 批量抓取并输出 Markdown
- YAML 头信息包含核心元数据

## 项目结构

```text
law-crawler/
├── law_crawler/
│   ├── cli.py
│   ├── crawler.py
│   ├── extractor.py
│   ├── markdown_writer.py
│   ├── models.py
│   └── sources/
│       └── gov_cn.py
├── tests/
├── requirements.txt
└── README.md
```

## 安装

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 第一阶段使用方式

### 1) 关键词批量抓取（gov.cn）

```bash
python -m law_crawler.cli \
  --keyword "安全生产法" \
  --sources gov.cn \
  --max-pages 3 \
  --max-items 30
```

### 2) URL 直抓（保留能力）

```bash
python -m law_crawler.cli \
  --url "https://www.gov.cn/zhengce/2024-01/01/content_xxx.htm" \
  --url "https://www.mem.gov.cn/xxgk/zfxxgkpt/fdzdgknr/202402/t20240220_xxx.shtml"
```

### 3) 输出目录与抓取参数

```bash
python -m law_crawler.cli \
  --keyword "行政法规" \
  --output-dir output \
  --sleep-seconds 1.0 \
  --retries 3
```

## 输出目录结构（第一阶段）

```text
output/
├── regulations/
│   └── {year}/
│       └── {source_site}/
│           └── {filename}.md
└── notices/
    └── {year}/
        └── {source_site}/
            └── {filename}.md
```

## Markdown YAML 头（第一阶段）

每个文件至少包含：

- `title`
- `doc_type`
- `category`
- `issuer`
- `publish_date`
- `source_site`
- `source_url`
- `keyword`
- `crawled_at`

示例：

```yaml
---
title: 中华人民共和国安全生产法
doc_type: law_or_regulation
category: regulations
issuer: 全国人民代表大会常务委员会
publish_date: '2021-06-10'
source_site: www_gov_cn
source_url: https://www.gov.cn/...
keyword: 安全生产法
crawled_at: '2026-03-07T09:30:00.000000Z'
---
```

## 本地验证

```bash
python -m compileall law_crawler tests
python -m unittest discover -s tests -p "test_*.py"
python -m law_crawler.cli --help
```
