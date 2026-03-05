from __future__ import annotations

import re
from typing import Optional

from bs4 import BeautifulSoup
from markdownify import markdownify as md


class ContentExtractor:
    """从复杂页面中提取正文区域并转换成 Markdown。"""

    MAIN_SELECTORS = [
        "article",
        ".article",
        ".article-content",
        ".content",
        ".TRS_Editor",
        "#UCAP-CONTENT",
        ".pages_content",
        ".detail-content",
        ".policy-content",
        "main",
    ]

    def extract_html_content(self, html: str) -> str:
        soup = BeautifulSoup(html, "lxml")
        self._remove_noise(soup)

        for selector in self.MAIN_SELECTORS:
            node = soup.select_one(selector)
            if node and len(node.get_text(strip=True)) > 120:
                return str(node)

        body = soup.body or soup
        return str(body)

    def html_to_markdown(self, html_fragment: str) -> str:
        markdown = md(html_fragment, heading_style="ATX")
        return self._cleanup_markdown(markdown)

    @staticmethod
    def classify_content(title: str, markdown_text: str) -> str:
        full_text = f"{title}\n{markdown_text}".lower()

        standard_keywords = ["国家标准", "gb/t", "gb ", "标准"]
        law_keywords = ["法", "条例", "司法解释", "法律"]
        regulation_keywords = ["通知", "意见", "办法", "规定", "政策", "公告", "决定"]

        if any(k in full_text for k in (kw.lower() for kw in standard_keywords)):
            return "standard"
        if any(k in full_text for k in (kw.lower() for kw in law_keywords)):
            return "law"
        if any(k in full_text for k in (kw.lower() for kw in regulation_keywords)):
            return "regulation"
        return "other"

    @staticmethod
    def _remove_noise(soup: BeautifulSoup) -> None:
        for selector in [
            "script",
            "style",
            "noscript",
            "iframe",
            "header",
            "footer",
            ".share",
            ".breadcrumb",
            ".nav",
            ".ad",
            ".advertisement",
        ]:
            for node in soup.select(selector):
                node.decompose()

    @staticmethod
    def _cleanup_markdown(text: str) -> str:
        text = re.sub(r"\n{3,}", "\n\n", text)
        text = re.sub(r"[ \t]+\n", "\n", text)
        return text.strip() + "\n"
