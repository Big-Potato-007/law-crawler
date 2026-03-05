from __future__ import annotations

import re
import time
from typing import Iterable, List, Optional
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

from .models import CrawlResult, SearchConfig
from .sources import SOURCE_REGISTRY

DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
    )
}


class WebCrawler:
    def __init__(self, timeout: int = 15, sleep_seconds: float = 0.8, retries: int = 2) -> None:
        self.timeout = timeout
        self.sleep_seconds = sleep_seconds
        self.retries = retries
        self.session = requests.Session()
        self.session.headers.update(DEFAULT_HEADERS)

    def fetch_html(self, url: str) -> Optional[str]:
        for attempt in range(self.retries + 1):
            try:
                resp = self.session.get(url, timeout=self.timeout)
                resp.raise_for_status()
                if "text/html" in resp.headers.get("Content-Type", ""):
                    resp.encoding = resp.apparent_encoding or resp.encoding
                    return resp.text
                return None
            except requests.RequestException:
                if attempt >= self.retries:
                    return None
                time.sleep(self.sleep_seconds)
        return None

    def search(self, config: SearchConfig) -> List[str]:
        source_adapter = SOURCE_REGISTRY.get(config.source)
        if not source_adapter:
            raise ValueError(f"Unsupported source: {config.source}")

        links: List[str] = []
        seen = set()
        for page in range(1, config.max_pages + 1):
            search_url = source_adapter.build_search_url(config.keyword, page)
            html = self.fetch_html(search_url)
            if not html:
                continue

            page_links = source_adapter.parse_search_links(html)
            for link in page_links:
                if link not in seen:
                    seen.add(link)
                    links.append(link)

            time.sleep(self.sleep_seconds)

        return links

    def crawl_urls(
        self,
        urls: Iterable[str],
        source_fallback: str = "unknown",
        keyword: Optional[str] = None,
        max_items: int = 20,
    ) -> List[CrawlResult]:
        results: List[CrawlResult] = []

        for idx, url in enumerate(urls):
            if idx >= max_items:
                break

            html = self.fetch_html(url)
            if not html:
                continue

            soup = BeautifulSoup(html, "lxml")
            title = self._extract_title(soup) or url
            source_site = self._detect_source_site(url) or source_fallback
            published_at = self._extract_date(soup, html)

            results.append(
                CrawlResult(
                    title=title,
                    url=url,
                    source_site=source_site,
                    html=html,
                    published_at=published_at,
                    keyword=keyword,
                )
            )
            time.sleep(self.sleep_seconds)

        return results

    @staticmethod
    def _extract_title(soup: BeautifulSoup) -> Optional[str]:
        for selector in ["h1", "meta[property='og:title']", "title"]:
            node = soup.select_one(selector)
            if not node:
                continue
            if node.name == "meta":
                content = (node.get("content") or "").strip()
                if content:
                    return content
            else:
                text = node.get_text(" ", strip=True)
                if text:
                    return text
        return None

    @staticmethod
    def _detect_source_site(url: str) -> Optional[str]:
        netloc = urlparse(url).netloc.lower()
        return netloc.replace(".", "_") if netloc else None

    @staticmethod
    def _extract_date(soup: BeautifulSoup, html: str) -> Optional[str]:
        meta_candidates = [
            "meta[name='PubDate']",
            "meta[name='publishdate']",
            "meta[name='publish-date']",
            "meta[property='article:published_time']",
        ]
        for selector in meta_candidates:
            node = soup.select_one(selector)
            if node:
                content = (node.get("content") or "").strip()
                if content:
                    return content[:10]

        date_patterns = [
            r"(20\d{2}-\d{1,2}-\d{1,2})",
            r"(20\d{2}/\d{1,2}/\d{1,2})",
            r"(20\d{2}年\d{1,2}月\d{1,2}日)",
        ]
        text = soup.get_text(" ", strip=True)
        for pattern in date_patterns:
            match = re.search(pattern, text) or re.search(pattern, html)
            if match:
                return match.group(1).replace("年", "-").replace("月", "-").replace("日", "")
        return None
