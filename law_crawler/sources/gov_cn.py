from __future__ import annotations

from typing import List, Optional, Set
from urllib.parse import quote_plus, urljoin, urlparse

from bs4 import BeautifulSoup


class GovCnSource:
    base_url = "https://www.gov.cn"

    def build_search_url(self, keyword: str, page: int) -> str:
        return f"{self.base_url}/search/zhengce/?t=zhengce&q={quote_plus(keyword)}&p={page}"

    def parse_search_links(self, html: str) -> List[str]:
        soup = BeautifulSoup(html, "lxml")
        links: List[str] = []
        seen: Set[str] = set()

        selectors = [
            ".middle_result_con.show li h4 a",
            ".result li a",
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

        return links

    def _normalize_url(self, href: str) -> Optional[str]:
        href = href.strip()
        if not href or href.startswith("javascript:"):
            return None
        full = urljoin(self.base_url, href)
        return full if full.startswith("http") else None

    @staticmethod
    def _is_policy_like_url(url: str) -> bool:
        parsed = urlparse(url)
        if not parsed.netloc.endswith("gov.cn"):
            return False
        policy_path_keywords = ["zhengce", "content", "flfg", "law", "standard", "biaozhun"]
        path = parsed.path.lower()
        return any(k in path for k in policy_path_keywords)
