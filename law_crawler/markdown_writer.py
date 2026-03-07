from __future__ import annotations

import re
from pathlib import Path

import yaml

from .models import ParsedDocument, build_output_folder


class MarkdownWriter:
    def __init__(self, output_dir: str = "output") -> None:
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def save_document(self, doc: ParsedDocument) -> Path:
        folder = build_output_folder(
            base_dir=str(self.output_dir),
            category=doc.category,
            publish_date=doc.publish_date,
            crawled_at=doc.crawled_at,
            source_site=doc.source_site,
        )
        folder.mkdir(parents=True, exist_ok=True)

        base_name = self._sanitize_filename(doc.title) + ".md"
        file_path = self._resolve_unique_path(folder / base_name)

        front_matter = {
            "title": doc.title,
            "doc_type": doc.doc_type,
            "category": doc.category,
            "issuer": doc.issuer,
            "publish_date": doc.publish_date,
            "source_site": doc.source_site,
            "source_url": doc.source_url,
            "keyword": doc.keyword,
            "crawled_at": doc.crawled_at.isoformat() + "Z",
        }

        content = self._build_markdown(front_matter, doc.markdown_content)
        file_path.write_text(content, encoding="utf-8")
        return file_path

    @staticmethod
    def _build_markdown(front_matter: dict, body: str) -> str:
        yaml_block = yaml.safe_dump(
            front_matter,
            sort_keys=False,
            allow_unicode=True,
            default_flow_style=False,
        ).strip()
        return f"---\n{yaml_block}\n---\n\n{body}"

    @staticmethod
    def _sanitize_filename(name: str, max_len: int = 80) -> str:
        safe = re.sub(r"[\\/:*?\"<>|]+", "_", name).strip(" .")
        safe = re.sub(r"\s+", "_", safe)
        return (safe[:max_len] or "untitled").strip("_")

    @staticmethod
    def _resolve_unique_path(path: Path) -> Path:
        if not path.exists():
            return path

        stem = path.stem
        suffix = path.suffix
        parent = path.parent
        counter = 2
        while True:
            candidate = parent / f"{stem}_{counter}{suffix}"
            if not candidate.exists():
                return candidate
            counter += 1
