"""
ツール②: 契約書・規約サマリーBot
"""

import streamlit as st
import sys, os

sys.path.append(os.path.join(os.path.dirname(__file__), "../.."))

from src.sommon.llm import chat_json
from src.sommon.ui import page_header
from src.sommon.file_utils import extract_pdf_text, split_into_chunks


def render():
    page_header(
        "📄",
        "契約書・規約サマリーBot",
        "PDFをアップロードするだけでリスク箇所・重要条項を自動整理します",
    )

    uploaded = st.file_uploader("契約書PDFをアップロード", type=["pdf"])
    if not uploaded:
        return

    with st.spinner("PDFを読み込み中..."):
        raw_text = extract_pdf_text(uploaded)
        chunks = split_into_chunks(raw_text)

    st.info(f"📖 {len(raw_text):,} 文字 ／ {len(chunks)} チャンクに分割")

    if not st.button("⚡ 分析する", type="primary"):
        return

    results = []
    progress = st.progress(0, text="分析中...")

    for i, chunk in enumerate(chunks):
        data = chat_json(f"""
以下は契約書・規約の一部です。重要な情報を抽出しJSONで返してください。

## 出力形式（JSONのみ）
{{
  "重要条項": ["条項1", "条項2"],
  "リスク箇所": ["リスク1", "リスク2"],
  "要注意ワード": ["ワード1", "ワード2"]
}}

該当なければ空リスト [] を返してください。

## 契約書テキスト
{chunk}
""")
        results.append(data)
        progress.progress((i + 1) / len(chunks), text=f"分析中... {i+1}/{len(chunks)}")

    progress.empty()

    # マージ・重複除去
    merged = {"重要条項": [], "リスク箇所": [], "要注意ワード": []}
    for r in results:
        for key in merged:
            merged[key].extend(r.get(key, []))
    for key in merged:
        merged[key] = list(dict.fromkeys(merged[key]))

    st.success("✅ 分析完了！")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 📌 重要条項")
        for item in merged["重要条項"]:
            st.markdown(f"- {item}")
        st.markdown("### ⚠️ リスク箇所")
        for item in merged["リスク箇所"]:
            st.error(item)

    with col2:
        st.markdown("### 🔍 要注意ワード")
        for word in merged["要注意ワード"]:
            st.warning(word)

    with st.expander("📃 抽出テキスト全文（先頭3,000文字）"):
        st.text(raw_text[:3000] + "...")
