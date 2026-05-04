"""
ツール③: CSV → 分析レポート自動生成Bot
"""

import streamlit as st
import matplotlib.pyplot as plt
import sys, os

sys.path.append(os.path.join(os.path.dirname(__file__), "../.."))

from src.sommon.llm import chat_json
from src.sommon.ui import page_header
from src.sommon.file_utils import read_csv, df_to_csv_bytes

try:
    import japanize_matplotlib  # noqa
except ImportError:
    pass


def _summarize_df(df) -> str:
    lines = [
        f"行数: {len(df)}, 列数: {len(df.columns)}",
        f"列名: {list(df.columns)}",
        "\n## 数値列の統計",
        df.describe().to_string(),
        "\n## 先頭5行",
        df.head().to_string(),
    ]
    return "\n".join(lines)


def _plot_histograms(df):
    num_cols = df.select_dtypes(include="number").columns.tolist()[:3]
    if not num_cols:
        return
    fig, axes = plt.subplots(1, len(num_cols), figsize=(14, 4))
    if len(num_cols) == 1:
        axes = [axes]
    for ax, col in zip(axes, num_cols):
        ax.hist(df[col].dropna(), bins=20, color="#2563eb", edgecolor="white")
        ax.set_title(col, fontsize=12)
        ax.set_ylabel("件数")
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()


def render():
    page_header(
        "📊",
        "CSV → 分析レポート自動生成Bot",
        "CSVをアップロードするだけでグラフとAIインサイトを自動生成します",
    )

    uploaded = st.file_uploader("CSVファイルをアップロード", type=["csv"])
    if not uploaded:
        return

    df = read_csv(uploaded)
    st.success(f"✅ 読み込み完了：{len(df):,} 行 × {len(df.columns)} 列")
    st.markdown("### 👀 データプレビュー")
    st.dataframe(df.head(10), use_container_width=True)

    if not st.button("⚡ 分析レポートを生成する", type="primary"):
        return

    st.markdown("### 📈 数値列の分布")
    _plot_histograms(df)

    with st.spinner("Claude がインサイトを生成中..."):
        data = chat_json(f"""
以下はCSVデータの概要です。ビジネス観点で分析し、JSONで返してください。

## 出力形式（JSONのみ）
{{
  "全体サマリー": "データ全体の特徴を3行で",
  "注目ポイント": ["発見1", "発見2", "発見3"],
  "推奨アクション": ["アクション1", "アクション2"],
  "データ品質の懸念": ["懸念1"]
}}

## データ概要
{_summarize_df(df)}
""")

    st.markdown("### 🧠 AIインサイト")
    st.info(data.get("全体サマリー", ""))

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### 🔍 注目ポイント")
        for p in data.get("注目ポイント", []):
            st.markdown(f"- {p}")
        st.markdown("#### ✅ 推奨アクション")
        for a in data.get("推奨アクション", []):
            st.markdown(f"- {a}")
    with col2:
        st.markdown("#### ⚠️ データ品質の懸念")
        for c in data.get("データ品質の懸念", []):
            st.warning(c)

    st.markdown("### 💾 統計情報をダウンロード")
    st.download_button(
        "📥 統計サマリーCSV",
        data=df.describe().to_csv().encode("utf-8-sig"),
        file_name="stats_summary.csv",
        mime="text/csv",
    )
