'''共通ベースクラスとデータ構造'''

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple


@dataclass
class Finding:
    '''隠匿テキスト検出結果'''
    location: str
    snippet: str


class BaseScanner(ABC):
    '''Scanner 抽象基底クラス'''

    @abstractmethod
    def scan(self, path: Path) -> Tuple[bool, List[Finding]]:
        '''ファイルを走査し、隠匿テキストがあれば (True, findings) を返す'''
        pass