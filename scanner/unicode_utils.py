'''Unicode 制御文字 & 色コントラスト関数'''

import unicodedata
from typing import List, Tuple

# 透過度とコントラストの閾値
ALPHA_THRESHOLD = 0.15          # 15% 未満なら「ほぼ透明」
CONTRAST_THRESHOLD = 1.3        # WCAG 比で 1.3:1 未満は肉眼でほぼ判別不能
MIN_FONT_PT = 4                 # 4pt 以下は“極小フォント”扱い なお、4ptは1文字辺り約1.41mm程度


def contains_invisible_unicode(text: str) -> bool:
    '''ゼロ幅・制御系 Unicode (Cf, Zl, Zp) を含むか判定'''
    return any(unicodedata.category(ch) in {"Cf", "Zl", "Zp"} for ch in text)


def extract_invisible_unicode(text: str) -> List[str]:
    '''不可視 Unicode をすべてリスト化'''
    return [ch for ch in text if unicodedata.category(ch) in {"Cf", "Zl", "Zp"}]


def rgb_to_luminance(r: int, g: int, b: int) -> float:
    '''WCAG 仕様に基づき相対輝度を計算する'''
    def _norm(c):  # 0-255 → 0-1 線形/ガンマ補正
        c = c / 255.0
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    r_l, g_l, b_l = map(_norm, (r, g, b))
    return 0.2126 * r_l + 0.7152 * g_l + 0.0722 * b_l


def contrast_ratio(rgb_fg: Tuple[int, int, int],
                   rgb_bg: Tuple[int, int, int] = (255, 255, 255)) -> float:
    '''前景と背景のコントラスト比 (1.0–21.0) を返す'''
    l1 = rgb_to_luminance(*rgb_fg) + 0.05
    l2 = rgb_to_luminance(*rgb_bg) + 0.05
    return max(l1, l2) / min(l1, l2)
