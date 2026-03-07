from datetime import datetime
import unittest

from law_crawler.models import build_output_folder, classify_doc_type_and_category


class Phase1LogicTests(unittest.TestCase):
    def test_law_goes_to_regulations(self):
        doc_type, category = classify_doc_type_and_category("中华人民共和国安全生产法", "")
        self.assertEqual(doc_type, "law_or_regulation")
        self.assertEqual(category, "regulations")

    def test_notice_goes_to_notices(self):
        doc_type, category = classify_doc_type_and_category("国务院关于加强安全生产工作的通知", "")
        self.assertEqual(doc_type, "notice_or_policy")
        self.assertEqual(category, "notices")

    def test_output_folder_structure(self):
        folder = build_output_folder(
            base_dir="output",
            category="regulations",
            publish_date="2021-06-10",
            crawled_at=datetime(2026, 3, 7, 10, 0, 0),
            source_site="www_gov_cn",
        )
        self.assertEqual(str(folder), "output/regulations/2021/www_gov_cn")


if __name__ == "__main__":
    unittest.main()
