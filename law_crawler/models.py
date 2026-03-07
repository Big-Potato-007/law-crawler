from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple


@dataclass
class SearchConfig:
    source: str
    keyword: str
    max_pages: int = 1


@dataclass
class CrawlResult:
    title: str
    url: str
    source_site: str
    html: str
    publish_date: Optional[str] = None
    keyword: Optional[str] = None
    issuer: Optional[str] = None
    doc_type: Optional[str] = None


@dataclass
class ParsedDocument:
    title: str
    source_url: str
    source_site: str
    category: str
    markdown_content: str
    crawled_at: datetime
    publish_date: Optional[str] = None
    keyword: Optional[str] = None
    issuer: Optional[str] = None
    doc_type: Optional[str] = None


def classify_doc_type_and_category(title: str, body_text: str = "") -> Tuple[str, str]:
    text = f"{title}\n{body_text}".lower()

    law_keywords = ["法", "条例", "行政法规", "规章", "司法解释", "实施细则", "实施办法"]
    notice_keywords = ["通知", "公告", "通告", "意见", "办法", "细则", "指南", "方案", "决定"]

    if any(k in text for k in (kw.lower() for kw in law_keywords)):
        return "law_or_regulation", "regulations"
    if any(k in text for k in (kw.lower() for kw in notice_keywords)):
        return "notice_or_policy", "notices"

    # 阶段一只有两类，默认归入 notices，避免误分到 standard/other。
    return "notice_or_policy", "notices"


def infer_issuer(title: str, fallback: str = "") -> Optional[str]:
    candidates = [
        "国务院",
        "应急管理部",
        "国家发展改革委",
        "国家市场监督管理总局",
        "财政部",
        "公安部",
        "工业和信息化部",
        "司法部",
        "人力资源社会保障部",
    ]
    text = f"{title} {fallback}"
    for item in candidates:
        if item in text:
            return item

    # 常见标题模式："XX关于..." -> issuer = XX
    match = re.match(r"^(.{2,25}?)(关于|印发|发布|公布)", title.strip())
    if match:
        return match.group(1)
    return None


def build_output_folder(base_dir: str, category: str, publish_date: Optional[str], crawled_at: datetime, source_site: str) -> Path:
    year = _extract_year(publish_date) or str(crawled_at.year)
    return Path(base_dir) / category / year / source_site


def _extract_year(publish_date: Optional[str]) -> Optional[str]:
    if not publish_date:
        return None
    match = re.search(r"(20\d{2})", publish_date)
    return match.group(1) if match else None
