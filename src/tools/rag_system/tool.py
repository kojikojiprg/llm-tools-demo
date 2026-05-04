"""
ツール⑥: 社内ナレッジ検索 RAGシステム
"""

import streamlit as st
import os, sys, tempfile

sys.path.append(os.path.join(os.path.dirname(__file__), "../.."))

from src.common.llm import chat
from src.common.ui import page_header
from src.tools.rag_system.rag import get_collection, index_document, search


def _rag_answer(query: str) -> dict:
    chunks = search(query)
    context = "\n\n---\n\n".join(
        f"【出典: {c['source']}】\n{c['text']}" for c in chunks
    )
    answer = chat(f"""以下の「参考ドキュメント」だけを根拠に質問に答えてください。
ドキュメントに答えが見つからない場合は「資料に記載がありません」と正直に答えてください。

## 参考ドキュメント
{context}

## 質問
{query}
""")
    return {"answer": answer, "chunks": chunks}


def render():
    page_header(
        "🤖",
        "社内ナレッジ検索 RAGシステム",
        "PDFやテキストを登録して、自然言語で質問・検索できます",
    )

    tab_search, tab_index = st.tabs(["💬 質問する", "📂 ドキュメント登録"])

    with tab_search:
        try:
            col = get_collection()
            count = col.count()
            st.info(f"📚 登録済みチャンク数: {count}")
        except Exception:
            st.warning("ChromaDBの初期化中です。先にドキュメントを登録してください。")
            return

        query = st.text_input(
            "質問を入力してください", placeholder="例：有給休暇の申請方法は？"
        )
        if st.button("🔍 検索して回答する", type="primary", disabled=not query):
            with st.spinner("検索＆回答生成中..."):
                result = _rag_answer(query)

            st.markdown("### 💬 回答")
            st.markdown(result["answer"])

            with st.expander("📎 参照したチャンク（根拠）"):
                for i, chunk in enumerate(result["chunks"]):
                    st.markdown(
                        f"**[{i+1}] 出典: {chunk['source']}**（類似度: {1 - chunk['score']:.3f}）"
                    )
                    st.text(chunk["text"][:300] + "...")
                    st.divider()

    with tab_index:
        uploaded = st.file_uploader(
            "登録するファイル（PDF / txt）",
            type=["pdf", "txt"],
            accept_multiple_files=True,
        )
        if uploaded and st.button("📥 DBに登録する", type="primary"):
            for f in uploaded:
                suffix = "." + f.name.split(".")[-1]
                with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                    tmp.write(f.read())
                    tmp_path = tmp.name
                with st.spinner(f"{f.name} を登録中..."):
                    n = index_document(tmp_path)
                    os.unlink(tmp_path)
                st.success(f"✅ {f.name}（{n} チャンク）を登録しました")
            st.rerun()
