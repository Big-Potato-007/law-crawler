from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


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
    published_at: Optional[str] = None
    keyword: Optional[str] = None


@dataclass
class ParsedDocument:
    title: str
    source_url: str
    source_site: str
    category: str
    markdown_content: str
    crawled_at: datetime
    published_at: Optional[str] = None
    keyword: Optional[str] = None
