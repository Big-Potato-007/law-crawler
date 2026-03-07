from __future__ import annotations

import argparse
from datetime import datetime
from typing import List, Protocol, Set

from .models import ParsedDocument, SearchConfig, classify_doc_type_and_category


class SearchCrawler(Protocol):
    def search(self, config: SearchConfig) -> List[str]:
        ...


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="抓取中央法规/中央通知并输出 Markdown")
    parser.add_argument("--keyword", type=str, help="检索关键词，例如：食品安全法")
    parser.add_argument("--sources", nargs="+", default=["gov.cn"], help="检索站点，当前内置: gov.cn")
    parser.add_argument("--url", action="append", default=[], help="直接抓取指定 URL，可重复")
    parser.add_argument("--max-pages", type=int, default=1, help="每个来源最大检索页数")
    parser.add_argument("--max-items", type=int, default=20, help="最大抓取条目数")
    parser.add_argument("--output-dir", type=str, default="output", help="Markdown 输出目录")
    parser.add_argument("--timeout", type=int, default=15, help="HTTP 请求超时（秒）")
    parser.add_argument("--sleep-seconds", type=float, default=0.8, help="请求间隔秒数")
    parser.add_argument("--retries", type=int, default=2, help="请求失败重试次数")
    return parser.parse_args()


def collect_urls(crawler: SearchCrawler, args: argparse.Namespace) -> List[str]:
    urls: List[str] = []

    if args.keyword:
        for source in args.sources:
            found = crawler.search(SearchConfig(source=source, keyword=args.keyword, max_pages=args.max_pages))
            urls.extend(found)

    urls.extend(args.url)

    deduped: List[str] = []
    seen: Set[str] = set()
    for url in urls:
        if url not in seen:
            seen.add(url)
            deduped.append(url)
    return deduped[: args.max_items]


def main() -> None:
    args = parse_args()

    try:
        from .crawler import WebCrawler
        from .extractor import ContentExtractor
        from .markdown_writer import MarkdownWriter
    except ModuleNotFoundError as exc:
        print(
            "缺少依赖，请先安装 requirements.txt 后再运行。\n"
            f"当前缺失模块：{exc.name}"
        )
        return

    crawler = WebCrawler(timeout=args.timeout, sleep_seconds=args.sleep_seconds, retries=args.retries)
    extractor = ContentExtractor()
    writer = MarkdownWriter(output_dir=args.output_dir)

    urls = collect_urls(crawler, args)
    if not urls:
        print("未获取到可抓取的 URL，请检查关键词、来源站点，或改用 --url 直接输入页面地址。")
        return

    crawled = crawler.crawl_urls(
        urls,
        source_fallback=(args.sources[0] if args.sources else "unknown"),
        keyword=args.keyword,
        max_items=args.max_items,
    )
    if not crawled:
        print("抓取失败：没有成功下载任何页面。")
        return

    saved_files: List[str] = []
    for item in crawled:
        html_main = extractor.extract_html_content(item.html)
        markdown_body = extractor.html_to_markdown(html_main)
        doc_type, category = classify_doc_type_and_category(item.title, markdown_body)

        path = writer.save_document(
            ParsedDocument(
                title=item.title,
                source_url=item.url,
                source_site=item.source_site,
                category=category,
                markdown_content=markdown_body,
                crawled_at=datetime.utcnow(),
                publish_date=item.publish_date,
                keyword=item.keyword,
                issuer=item.issuer,
                doc_type=doc_type,
            )
        )
        saved_files.append(str(path))

    print(f"抓取完成，共保存 {len(saved_files)} 个 Markdown 文件：")
    for item in saved_files:
        print(f"- {item}")


if __name__ == "__main__":
    main()
