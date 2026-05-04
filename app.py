"""
AI Tools Suite - メインアプリ
サイドバーナビゲーションで6つのツールを切り替える
"""

import streamlit as st
import sys, os

sys.path.append(os.path.dirname(__file__))

from src.sommon.ui import inject_global_css

# ページ設定
st.set_page_config(
    page_title="AI Tools Suite",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_global_css()

# ナビゲーション定義
TOOLS = [
    {
        "key": "home",
        "icon": "🏠",
        "label": "ホーム",
        "phase": None,
    },
    {
        "key": "minutes",
        "icon": "🎙️",
        "label": "議事録Bot",
        "phase": "Phase 1",
        "desc": "議事録 → アクションアイテム抽出",
    },
    {
        "key": "contract",
        "icon": "📄",
        "label": "契約書Bot",
        "phase": "Phase 1",
        "desc": "PDF → リスク・重要条項サマリー",
    },
    {
        "key": "csv",
        "icon": "📊",
        "label": "CSV分析Bot",
        "phase": "Phase 2",
        "desc": "CSV → グラフ＋AIインサイト",
    },
    {
        "key": "ga4",
        "icon": "📈",
        "label": "GA4×Slack",
        "phase": "Phase 2",
        "desc": "週次レポート自動Slack投稿",
    },
    {
        "key": "anomaly",
        "icon": "🛒",
        "label": "異常検知Bot",
        "phase": "Phase 3",
        "desc": "時系列データの異常＋原因仮説",
    },
    {
        "key": "rag",
        "icon": "🤖",
        "label": "RAGシステム",
        "phase": "Phase 3",
        "desc": "社内ナレッジ検索",
    },
]

PHASE_COLORS = {
    "Phase 1": "#10b981",
    "Phase 2": "#2563eb",
    "Phase 3": "#ef4444",
}

# セッション初期化
if "current_tool" not in st.session_state:
    st.session_state.current_tool = "home"

# サイドバー
with st.sidebar:
    st.markdown(
        """
<div style="padding: 8px 0 20px;">
  <div style="font-size:24px; font-weight:800; color:#0f172a; letter-spacing:-0.5px;">
    🤖 AI Tools Suite
  </div>
  <div style="font-size:12px; color:#64748b; margin-top:4px;">
    AIエンジニア副業デモ集
  </div>
</div>
""",
        unsafe_allow_html=True,
    )

    current_phase = None
    for tool in TOOLS:
        # フェーズ区切り
        if tool["phase"] and tool["phase"] != current_phase:
            current_phase = tool["phase"]
            color = PHASE_COLORS.get(current_phase, "#64748b")
            st.markdown(
                f"""
<div style="font-size:10px; font-weight:700; color:{color};
     text-transform:uppercase; letter-spacing:1px;
     margin: 16px 0 6px 4px;">
  {current_phase}
</div>
""",
                unsafe_allow_html=True,
            )

        is_active = st.session_state.current_tool == tool["key"]
        active_style = (
            "background:#dbeafe; color:#1d4ed8; font-weight:700;"
            if is_active
            else "color:#475569;"
        )

        label_html = f"{tool['icon']} {tool['label']}"
        if tool.get("desc"):
            label_html += f'<div style="font-size:10px; color:#94a3b8; font-weight:400; margin-top:1px;">{tool["desc"]}</div>'

        if st.button(
            f"{tool['icon']} {tool['label']}",
            key=f"nav_{tool['key']}",
            use_container_width=True,
        ):
            st.session_state.current_tool = tool["key"]
            st.rerun()

    st.divider()
    st.markdown(
        """
<div style="font-size:11px; color:#94a3b8; padding: 4px 0;">
  Powered by Claude API<br>
  <code style="font-size:10px;">claude-sonnet-4-20250514</code>
</div>
""",
        unsafe_allow_html=True,
    )

# メインコンテンツ
key = st.session_state.current_tool

if key == "home":
    st.markdown(
        """
<div style="padding: 40px 0 24px;">
  <h1 style="font-size:36px; font-weight:800; margin:0; color:#0f172a;">
    🤖 AI Tools Suite
  </h1>
  <p style="font-size:16px; color:#64748b; margin-top:8px;">
    Python × LLM × データ分析で作る6つのビジネスツール
  </p>
</div>
""",
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns(3)
    cards = [
        (
            "🟢",
            "Phase 1 ─ 基礎固め",
            [
                ("🎙️", "議事録Bot", "LLM API・Streamlit・プロンプト設計"),
                ("📄", "契約書Bot", "PDFパース・チャンク分割"),
            ],
        ),
        (
            "🔵",
            "Phase 2 ─ データ×LLM",
            [
                ("📊", "CSV分析Bot", "Pandas・可視化・データ圧縮"),
                ("📈", "GA4×Slack", "外部API連携・定期実行"),
            ],
        ),
        (
            "🔴",
            "Phase 3 ─ 高度化",
            [
                ("🛒", "異常検知Bot", "時系列分析・統計的異常検知"),
                ("🤖", "RAGシステム", "Embeddings・ベクトルDB"),
            ],
        ),
    ]

    for col, (dot, phase_title, tools) in zip([col1, col2, col3], cards):
        with col:
            st.markdown(
                f"""
<div style="background:#fff; border:1px solid #e2e8f0; border-radius:12px;
     padding:20px; height:100%; box-shadow:0 1px 4px rgba(0,0,0,.05);">
  <div style="font-size:13px; font-weight:700; color:#64748b; margin-bottom:14px;">
    {dot} {phase_title}
  </div>
""",
                unsafe_allow_html=True,
            )
            for icon, name, desc in tools:
                st.markdown(
                    f"""
  <div style="display:flex; align-items:flex-start; gap:10px; margin-bottom:12px;">
    <span style="font-size:20px;">{icon}</span>
    <div>
      <div style="font-weight:700; font-size:14px;">{name}</div>
      <div style="font-size:12px; color:#94a3b8;">{desc}</div>
    </div>
  </div>
""",
                    unsafe_allow_html=True,
                )
            st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div style='margin-top:32px;'></div>", unsafe_allow_html=True)
    st.info("👈 サイドバーからツールを選択してください")

elif key == "minutes":
    from src.tools.minutes_bot.tool import render

    render()

elif key == "contract":
    from src.tools.contract_bot.tool import render

    render()

elif key == "csv":
    from src.tools.csv_analysis.tool import render

    render()

elif key == "ga4":
    from src.tools.ga4_slack.tool import render

    render()

elif key == "anomaly":
    from src.tools.anomaly_detection.tool import render

    render()

elif key == "rag":
    from src.tools.rag_system.tool import render

    render()
