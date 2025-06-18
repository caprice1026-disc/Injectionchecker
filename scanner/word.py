'''Word ファイル (.docx) に潜む隠匿テキストを検出する'''

from pathlib import Path
from zipfile import ZipFile
from typing import List, Tuple

from docx import Document
from docx.oxml.ns import qn  # type: ignore

from .base import BaseScanner, Finding
from .unicode_utils import (CONTRAST_THRESHOLD, MIN_FONT_PT,
                            contains_invisible_unicode, contrast_ratio,
                            extract_invisible_unicode)


class WordScanner(BaseScanner):
    '''.docx 専用スキャナ'''

    def scan(self, path: Path) -> Tuple[bool, List[Finding]]:
        '''隠匿テキストを検出'''
        findings: List[Finding] = []
        doc = Document(str(path))

        # 本文・テーブルなど Run 単位で検査
        for p_idx, para in enumerate(doc.paragraphs, 1):
            for run in para.runs:
                text = run.text or ""
                if not text.strip():
                    continue

                # 隠し文字属性
                is_hidden_flag = bool(getattr(run.font, "hidden", False))  # :contentReference[oaicite:1]{index=1}

                # フォントサイズ
                sz = run.font.size.pt if run.font.size else 11
                is_tiny = sz <= MIN_FONT_PT  # :contentReference[oaicite:2]{index=2}

                # 色と透過度
                col = run.font.color
                if col.type is None:  # デフォルト (黒)
                    rgb = (0, 0, 0)
                    alpha = 1.0
                else:
                    rgb = tuple(col.rgb[i] for i in range(3))  # type: ignore
                    alpha = getattr(col.rgb, "a", 1.0)

                is_low_contrast = contrast_ratio(rgb) < CONTRAST_THRESHOLD
                is_almost_transparent = alpha <= 255 * 0.15

                # 不可視 Unicode
                inv_unicode = contains_invisible_unicode(text)

                if any([is_hidden_flag, is_low_contrast, is_almost_transparent,
                        is_tiny, inv_unicode]):
                    snippet = (text[:40]
                               + (f" …+{len(text)-40}文字" if len(text) > 40 else ""))
                    findings.append(Finding(
                        location=f"段落 {p_idx}",
                        snippet=snippet
                    ))

        # customXml パーツも走査（python-docx が非対応） :contentReference[oaicite:3]{index=3}
        with ZipFile(path) as zf:
            for name in zf.namelist():
                if name.startswith("customXml/") and name.endswith(".xml"):
                    xml_body = zf.read(name).decode("utf-8", "ignore")
                    if xml_body.strip():
                        findings.append(Finding(
                            location=name,
                            snippet=xml_body[:40]
                        ))

        return (bool(findings), findings)
