"""
共通モジュール: ファイル処理ユーティリティ
"""
import fitz  # PyMuPDF
import pandas as pd
import io


def extract_pdf_text(uploaded_file) -> str:
    """StreamlitのUploadedFileからテキストを抽出する。"""
    pdf_bytes = uploaded_file.read()
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    return "\n".join(page.get_text() for page in doc)


def split_into_chunks(text: str, chunk_size: int = 3000) -> list[str]:
    """テキストをchunk_size文字ごとに分割する。"""
    words = text.split()
    chunks, current, length = [], [], 0
    for word in words:
        current.append(word)
        length += len(word) + 1
        if length >= chunk_size:
            chunks.append(" ".join(current))
            current, length = [], 0
    if current:
        chunks.append(" ".join(current))
    return chunks


def read_csv(uploaded_file) -> pd.DataFrame:
    """StreamlitのUploadedFileからDataFrameを読み込む。"""
    try:
        return pd.read_csv(uploaded_file, encoding="utf-8-sig")
    except UnicodeDecodeError:
        uploaded_file.seek(0)
        return pd.read_csv(uploaded_file, encoding="shift_jis")


def df_to_csv_bytes(df: pd.DataFrame) -> bytes:
    """DataFrameをExcel対応CSVバイト列に変換する。"""
    return df.to_csv(index=False).encode("utf-8-sig")
