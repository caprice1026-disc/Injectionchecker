import streamlit as st
from pathlib import Path
from tempfile import NamedTemporaryFile

from scanner.word import WordScanner
from scanner.pptx import PptxScanner
from scanner.pdf import PdfScanner

# サポートする拡張子ごとのスキャナ
SCANNERS = {
    ".docx": WordScanner(),
    ".pptx": PptxScanner(),
    ".pdf": PdfScanner(),
}


def show_header() -> None:
    """ヘッダー表示"""
    st.title("prompt-scanner")
    st.write(
        "アップロードしたドキュメントに\n\
        含まれる不可視テキストを検査するツールです。"
    )
    st.markdown(
        "1. `pptx` / `docx` / `pdf` を選択してアップロード\n"
        + "2. **スキャン開始** ボタンを押します"
    )


def show_footer() -> None:
    """フッター表示"""
    st.markdown("---")
    st.markdown(
        "ライセンス: AGPLv3 | "
        "[GitHub](https://github.com/example/repo) | "
        "[Twitter](https://twitter.com/example)"
    )


def run_scan(files: list) -> None:
    """アップロードされたファイルを走査"""
    progress = st.progress(0)
    status = st.empty()
    results = {}
    total = len(files)

    for idx, file in enumerate(files, start=1):
        ext = Path(file.name).suffix.lower()
        scanner = SCANNERS.get(ext)
        if scanner is None:
            st.warning(f"{file.name} は未対応形式です")
            continue

        with NamedTemporaryFile(delete=False, suffix=ext) as tmp:
            tmp.write(file.getbuffer())
            tmp_path = Path(tmp.name)

        status.write(f"{file.name} の視認不可能な文字を確認しています……")
        found, details = scanner.scan(tmp_path)
        status.write(f"{file.name} の不可視Unicodeを確認しています……")
        results[file.name] = (found, details)
        progress.progress(idx / total)
        tmp_path.unlink(missing_ok=True)

    progress.empty()
    status.empty()

    st.subheader("検査結果")
    if not results:
        st.info("アップロードされたファイルはありません")
        return
    for name, (found, details) in results.items():
        if not found:
            st.success(f"{name}: 問題は見つかりませんでした")
        else:
            st.error(f"{name}: 不可視テキストを検出")
            for d in details:
                st.write(f"- {d.location}: {d.snippet}")


def main() -> None:
    """メイン処理"""
    show_header()
    uploaded = st.file_uploader(
        "ファイルをアップロード",
        accept_multiple_files=True,
        type=["pptx", "docx", "pdf"],
    )

    if uploaded and st.button("スキャン開始"):
        run_scan(uploaded)

    show_footer()


if __name__ == "__main__":
    main()