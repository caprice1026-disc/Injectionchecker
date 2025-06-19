'''CLI で使用するときに使うスクリプト
   テストやデバッグに使用する予定

使い方:
    python -m scanner.cli test.docx
'''

import sys
from pathlib import Path
from scanner.word import WordScanner
from scanner.pptx import PptxScanner
from scanner.pdf import PdfScanner

scanners = {
    '.docx': WordScanner(),
    '.pptx': PptxScanner(),
    '.pdf':  PdfScanner(),
}

def quick_scan(file_path: Path):
    '''ファイルを走査して結果を stdout に出力'''
    scanner = scanners.get(file_path.suffix.lower())
    if scanner is None:
        print(f"[SKIP] 未対応拡張子: {file_path.name}")
        return

    found, details = scanner.scan(file_path)
    if found:
        print(f"[!] 隠匿テキストあり — {file_path.name}")
        for f in details:
            print(f"  - {f.location}: {f.snippet}")
    else:
        print(f"[OK] 問題なし — {file_path.name}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python -m scanner.cli <file1> [file2 ...]")
        sys.exit(1)

    for arg in sys.argv[1:]:
        quick_scan(Path(arg))
