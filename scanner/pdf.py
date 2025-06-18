'''PDF 内の不可視テキストをバイト列レベルで検出する'''

from pathlib import Path
from typing import List, Tuple
import re

from .base import BaseScanner, Finding
from .unicode_utils import contains_invisible_unicode

# 正規表現パターン
CA_PATTERN = re.compile(rb"/CA\s+0\.0?[0-7]\b")        # 塗り透明度 ~0–0.07
TR3_PATTERN = re.compile(rb"\b3\s+Tr\b")              # Text Rendering Mode 3 (invisible) :contentReference[oaicite:7]{index=7}
EMBED_JS_PATTERN = re.compile(rb"/JavaScript\s*<</", re.DOTALL)

class PdfScanner(BaseScanner):
    '''.pdf 専用スキャナ（簡易版）'''

    def scan(self, path: Path) -> Tuple[bool, List[Finding]]:
        findings: List[Finding] = []
        data = Path(path).read_bytes()

        # テキストレンダリング透過
        for m in CA_PATTERN.finditer(data):
            findings.append(Finding(
                location=f"offset {m.start()}",
                snippet=f"/CA 0… ({m.group(0)[:15]}…)".decode(errors="ignore")
            ))

        # Text Rendering Mode = 3
        for m in TR3_PATTERN.finditer(data):
            findings.append(Finding(
                location=f"offset {m.start()}",
                snippet="Tr 3 (文字非描画)"
            ))

        # 埋め込み JavaScript
        if EMBED_JS_PATTERN.search(data):  # :contentReference[oaicite:8]{index=8}
            findings.append(Finding(
                location="PDF JavaScript",
                snippet="埋め込み JavaScript 検出"
            ))

        # 不可視 Unicode
        text_strings = re.findall(rb"\(([^)]{1,120})\)", data)
        for s in text_strings:
            s_dec = s.decode("utf-8", "ignore")
            if contains_invisible_unicode(s_dec):
                findings.append(Finding(
                    location="ストリーム文字列",
                    snippet=s_dec[:40]
                ))

        return (bool(findings), findings)
