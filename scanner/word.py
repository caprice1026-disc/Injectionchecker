'''Word ファイル (.docx) に潜む隠匿テキストを検出する'''

from pathlib import Path
from zipfile import ZipFile
from typing import List, Tuple, cast

from docx import Document

from .base import BaseScanner, Finding
from .unicode_utils import (
    CONTRAST_THRESHOLD,
    MIN_FONT_PT,
    contains_invisible_unicode,
    contrast_ratio,
)

class WordScanner(BaseScanner):
    '''.docx 専用スキャナ'''

    def scan(self, path: Path) -> Tuple[bool, List[Finding]]:
        '''隠匿テキストを検出して (bool, findings) を返す'''
        findings: List[Finding] = []

        # ★ str(path) で型ヒント適合
        doc = Document(str(path))

        for p_idx, para in enumerate(doc.paragraphs, 1):
            for run in para.runs:
                text = run.text or ''
                if not text.strip():
                    continue

                # --- 各種フラグ ---
                hidden = bool(getattr(run.font, 'hidden', False))
                size_pt = run.font.size.pt if run.font.size else 11
                tiny = size_pt <= MIN_FONT_PT

                # --- 色 & 透過度の安全取得 ---
                col = run.font.color          # ColorFormat | None
                rgb: Tuple[int, int, int]
                alpha: float

                if col is None or col.rgb is None:
                    # ColorFormat が無い or RGB 未設定 → デフォルト黒
                    rgb = (0, 0, 0)
                    alpha = 1.0
                else:
                    # 型ヒント上は Tuple[int, ...] 扱いなので 3 要素に固定キャスト
                    rgb = cast(Tuple[int, int, int],
                               (col.rgb[0], col.rgb[1], col.rgb[2]))
                    alpha = getattr(col.rgb, 'a', 1.0)

                low_contrast = contrast_ratio(rgb) < CONTRAST_THRESHOLD
                almost_transparent = alpha <= 255 * 0.15
                invisible_ucd = contains_invisible_unicode(text)

                if any([hidden, tiny, low_contrast, almost_transparent, invisible_ucd]):
                    snippet = (text[:40]
                               + (f' …+{len(text) - 40}文字' if len(text) > 40 else ''))
                    findings.append(Finding(
                        location=f'段落 {p_idx}',
                        snippet=snippet
                    ))

        # --- customXml パーツ走査 ---
        with ZipFile(path) as zf:
            for name in zf.namelist():
                if name.startswith('customXml/') and name.endswith('.xml'):
                    xml_body = zf.read(name).decode('utf-8', 'ignore')
                    if xml_body.strip():
                        findings.append(Finding(
                            location=name,
                            snippet=xml_body[:40]
                        ))

        return (bool(findings), findings)
