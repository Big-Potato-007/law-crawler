from __future__ import annotations

import re
from typing import List, Optional, Set
from urllib.parse import quote_plus, urljoin, urlparse

from bs4 import BeautifulSoup


class GovCnSource:
    base_url = "https://www.gov.cn"

    def build_search_url(self, keyword: str, page: int) -> str:
        """Backward-compatible single URL builder."""
        return self.build_search_urls(keyword, page)[0]

    def build_search_urls(self, keyword: str, page: int) -> List[str]:
        """
        Build multiple candidate search URLs because gov.cn search routing changes frequently.
        """
        q = quote_plus(keyword)
        # Some pages are 1-based, some interfaces are 0-based.
        page_zero_based = max(page - 1, 0)
        return [
            f"{self.base_url}/search/zhengce/?t=zhengce&q={q}&p={page}",
            f"{self.base_url}/search/zhengce/?q={q}&p={page}",
            f"{self.base_url}/search/zhengce/?t=zhengce&q={q}&p={page_zero_based}",
        ]

    def parse_search_links(self, html: str) -> List[str]:
        soup = BeautifulSoup(html, "lxml")
        links: List[str] = []
        seen: Set[str] = set()

        selectors = [
            ".middle_result_con.show li h4 a",
            ".middle_result_con li h4 a",
            ".result li a",
            "h4 a",
            "a",
        ]
        for selector in selectors:
            for a_tag in soup.select(selector):
                full = self._normalize_url(a_tag.get("href") or "")
                if full and self._is_policy_like_url(full) and full not in seen:
                    seen.add(full)
                    links.append(full)
            if links:
                break

        # fallback: parse link-like strings from script blobs if anchors are dynamically rendered
        if not links:
            links.extend(self._extract_links_from_raw_html(html, seen))

        return links

    def _normalize_url(self, href: str) -> Optional[str]:
        href = href.strip()
        if not href or href.startswith("javascript:"):
            return None
        full = urljoin(self.base_url, href)
        return full if full.startswith("http") else None

    def _extract_links_from_raw_html(self, html: str, seen: Set[str]) -> List[str]:
        links: List[str] = []
        for match in re.findall(r"https?://[^\"'\s<>]+", html):
            if not self._is_policy_like_url(match):
                continue
            cleaned = match.rstrip('\\"\'.,)];')
            if cleaned not in seen:
                seen.add(cleaned)
                links.append(cleaned)
        return links

    @staticmethod
    def _is_policy_like_url(url: str) -> bool:
        parsed = urlparse(url)
        if not parsed.netloc.endswith("gov.cn"):
            return False
        policy_path_keywords = ["zhengce", "content", "flfg", "law", "fg", "gongbao"]
        path = parsed.path.lower()
        return any(k in path for k in policy_path_keywords)
