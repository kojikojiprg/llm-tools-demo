"""
ツール⑤: EC売上データ 異常検知＋原因仮説Bot
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import sys, os

sys.path.append(os.path.join(os.path.dirname(__file__), "../.."))

from src.sommon.llm import chat_json
from src.sommon.ui import page_header
from src.sommon.file_utils import read_csv
from src.tools.anomaly_detection.detector import detect_anomalies, build_anomaly_summary


def _plot(df, date_col, value_col):
    normal = df[~df["is_anomaly"]]
    anomaly = df[df["is_anomaly"]]
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=pd.concat([df[date_col], df[date_col][::-1]]),
            y=pd.concat(
                [
                    df["rolling_mean"] + 2 * df["rolling_std"],
                    (df["rolling_mean"] - 2 * df["rolling_std"])[::-1],
                ]
            ),
            fill="toself",
            fillcolor="rgba(37,99,235,0.08)",
            line=dict(color="rgba(0,0,0,0)"),
            name="±2σ範囲",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=df[date_col],
            y=df["rolling_mean"],
            line=dict(color="#2563eb", width=1.5, dash="dot"),
            name="移動平均",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=normal[date_col],
            y=normal[value_col],
            mode="lines+markers",
            line=dict(color="#64748b", width=1.5),
            marker=dict(size=4),
            name="通常",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=anomaly[date_col],
            y=anomaly[value_col],
            mode="markers",
            marker=dict(
                color="#ef4444", size=12, symbol="circle-open", line=dict(width=2)
            ),
            name="⚠️ 異常",
        )
    )
    fig.update_layout(
        title="時系列データと異常検知結果",
        xaxis_title="日付",
        yaxis_title=value_col,
        hovermode="x unified",
        legend=dict(orientation="h", y=-0.2),
        height=420,
    )
    st.plotly_chart(fig, use_container_width=True)


def render():
    page_header(
        "🛒",
        "EC売上データ 異常検知＋原因仮説Bot",
        "時系列データの異常を自動検知し、AIが原因仮説を生成します",
    )

    # サンプルデータ生成
    with st.expander("📥 サンプルCSVを生成して試す"):
        if st.button("サンプルデータを生成"):
            dates = pd.date_range("2024-01-01", periods=90)
            np.random.seed(42)
            sales = 100 + np.cumsum(np.random.randn(90) * 3)
            sales[20] += 60
            sales[45] -= 50
            sales[70] += 40
            sample = pd.DataFrame(
                {"date": dates.strftime("%Y-%m-%d"), "sales": sales.round(0)}
            )
            st.download_button(
                "📥 sample.csv",
                sample.to_csv(index=False).encode("utf-8-sig"),
                "sample.csv",
                "text/csv",
            )

    uploaded = st.file_uploader(
        "CSVファイルをアップロード（日付列＋数値列）", type=["csv"]
    )
    if not uploaded:
        return

    df_raw = read_csv(uploaded)
    st.dataframe(df_raw.head(), use_container_width=True)

    cols = df_raw.columns.tolist()
    c1, c2 = st.columns(2)
    with c1:
        date_col = st.selectbox("📅 日付列", cols)
    with c2:
        value_col = st.selectbox("📊 数値列", [c for c in cols if c != date_col])

    if not st.button("⚡ 異常検知＋仮説生成", type="primary"):
        return

    with st.spinner("異常検知中..."):
        df = detect_anomalies(df_raw, value_col, date_col)

    count = df["is_anomaly"].sum()
    st.success(f"✅ {count} 件の異常を発見")
    _plot(df, date_col, value_col)

    if count > 0:
        st.markdown("### ⚠️ 異常データ一覧")
        adf = df[df["is_anomaly"]][
            [date_col, value_col, "rolling_mean", "pct_change", "z_score"]
        ].copy()
        adf.columns = ["日付", "値", "移動平均", "変化率(%)", "Zスコア"]
        st.dataframe(
            adf.style.format(
                {
                    "値": "{:.1f}",
                    "移動平均": "{:.1f}",
                    "変化率(%)": "{:+.1f}",
                    "Zスコア": "{:.2f}",
                }
            ),
            use_container_width=True,
        )

    with st.spinner("Claude が原因仮説を生成中..."):
        summary = build_anomaly_summary(df, value_col, date_col)
        insight = chat_json(f"""
以下はEC売上データの異常検知結果です。ビジネス観点で原因仮説と対策をJSONで返してください。

## 出力形式（JSONのみ）
{{
  "全体評価": "データ全体の傾向を2〜3行で",
  "異常の原因仮説": [
    {{
      "日付": "YYYY-MM-DD",
      "種別": "急騰 or 急落",
      "仮説": "考えられる原因",
      "確認方法": "検証に必要なデータ"
    }}
  ],
  "推奨アクション": ["アクション1", "アクション2"],
  "監視強化すべき指標": ["指標1", "指標2"]
}}

## 異常検知サマリー
{summary}
""")

    st.markdown("### 🧠 AIによる原因仮説")
    st.info(insight.get("全体評価", ""))

    st.markdown("#### 🔍 各異常の仮説")
    for item in insight.get("異常の原因仮説", []):
        with st.expander(f"📅 {item.get('日付','')}｜{item.get('種別','')}"):
            st.markdown(f"**仮説：** {item.get('仮説','')}")
            st.markdown(f"**確認方法：** {item.get('確認方法','')}")

    ca, cb = st.columns(2)
    with ca:
        st.markdown("#### ✅ 推奨アクション")
        for a in insight.get("推奨アクション", []):
            st.markdown(f"- {a}")
    with cb:
        st.markdown("#### 📡 監視強化すべき指標")
        for m in insight.get("監視強化すべき指標", []):
            st.markdown(f"- {m}")
