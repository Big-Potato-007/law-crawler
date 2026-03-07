import argparse
import unittest

from law_crawler.cli import collect_urls


class FakeCrawler:
    def __init__(self, mapping):
        self.mapping = mapping

    def search(self, config):
        return self.mapping.get((config.source, config.keyword, config.max_pages), [])


class CollectUrlsTests(unittest.TestCase):
    def test_collect_urls_deduplicates_and_limits(self):
        args = argparse.Namespace(
            keyword="食品安全法",
            sources=["gov.cn"],
            url=["https://a", "https://b", "https://a"],
            max_pages=1,
            max_items=3,
        )
        crawler = FakeCrawler({("gov.cn", "食品安全法", 1): ["https://x", "https://a", "https://y"]})

        urls = collect_urls(crawler, args)
        self.assertEqual(urls, ["https://x", "https://a", "https://y"])

    def test_collect_urls_supports_url_only_mode(self):
        args = argparse.Namespace(
            keyword=None,
            sources=["gov.cn"],
            url=["https://a", "https://a", "https://b"],
            max_pages=1,
            max_items=10,
        )
        crawler = FakeCrawler({})

        urls = collect_urls(crawler, args)
        self.assertEqual(urls, ["https://a", "https://b"])

    def test_collect_urls_returns_empty_when_no_keyword_and_no_url(self):
        args = argparse.Namespace(
            keyword=None,
            sources=["gov.cn"],
            url=[],
            max_pages=1,
            max_items=10,
        )
        crawler = FakeCrawler({})

        urls = collect_urls(crawler, args)
        self.assertEqual(urls, [])


if __name__ == "__main__":
    unittest.main()
