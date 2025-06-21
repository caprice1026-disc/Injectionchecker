# prompt-scanner

このプロジェクトは Word、PowerPoint、PDF から人間には見えないテキストを検出するツールです。

## インストール

```bash
pip install -r requirements.txt
```

Python 3.9 以上を推奨しています。

## 使い方

### Streamlit アプリとして実行

```bash
python app.py
```

ブラウザ上でファイルをアップロードしてスキャンできます。

### コマンドラインからの利用

```bash
python -m scanner.cli <file1> [file2 ...]
```

走査結果が標準出力に表示されます。

## ディレクトリ構成

```
scanner/
  base.py          共通データクラスと抽象クラス
  word.py          Word 走査ロジック
  pptx.py          PowerPoint 走査ロジック
  pdf.py           PDF 走査ロジック
  unicode_utils.py Unicode 判定と色計算
app.py             Streamlit UI
```

## ライセンス

本ソフトウェアは AGPLv3 で提供されています。
