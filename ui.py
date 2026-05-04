"""
共通モジュール: Streamlit UIスタイル・ヘルパー
"""
import streamlit as st

GLOBAL_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;500;700&family=JetBrains+Mono:wght@400;600&display=swap');

:root {
    --primary:   #2563eb;
    --primary-light: #dbeafe;
    --accent:    #0ea5e9;
    --danger:    #ef4444;
    --warning:   #f59e0b;
    --success:   #10b981;
    --surface:   #f8fafc;
    --border:    #e2e8f0;
    --text:      #0f172a;
    --muted:     #64748b;
}

html, body, [class*="css"] {
    font-family: 'Noto Sans JP', sans-serif;
    color: var(--text);
}

/* サイドバーナビ */
.nav-item {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 10px 14px;
    border-radius: 8px;
    margin-bottom: 4px;
    cursor: pointer;
    font-weight: 500;
    font-size: 14px;
    color: var(--muted);
    transition: all .15s;
}
.nav-item:hover  { background: var(--primary-light); color: var(--primary); }
.nav-item.active { background: var(--primary-light); color: var(--primary); font-weight: 700; }

/* カード */
.card {
    background: #fff;
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 20px 24px;
    margin-bottom: 16px;
    box-shadow: 0 1px 4px rgba(0,0,0,.05);
}
.card-title { font-size: 16px; font-weight: 700; margin-bottom: 6px; }
.card-body  { font-size: 14px; color: var(--muted); line-height: 1.7; }

/* バッジ */
.badge {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 20px;
    font-size: 11px;
    font-weight: 700;
}
.badge-blue   { background: #dbeafe; color: #1d4ed8; }
.badge-green  { background: #d1fae5; color: #065f46; }
.badge-red    { background: #fee2e2; color: #991b1b; }
.badge-yellow { background: #fef3c7; color: #92400e; }

/* ページタイトル */
.page-header {
    display: flex;
    align-items: center;
    gap: 12px;
    padding-bottom: 16px;
    border-bottom: 2px solid var(--border);
    margin-bottom: 24px;
}
.page-icon  { font-size: 32px; }
.page-title { font-size: 22px; font-weight: 700; margin: 0; }
.page-desc  { font-size: 13px; color: var(--muted); margin: 2px 0 0; }

/* ボタン */
.stButton > button {
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-family: 'Noto Sans JP', sans-serif !important;
}

/* コード */
code { font-family: 'JetBrains Mono', monospace; font-size: 13px; }
</style>
"""


def inject_global_css():
    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)


def page_header(icon: str, title: str, desc: str):
    st.markdown(f"""
<div class="page-header">
  <span class="page-icon">{icon}</span>
  <div>
    <p class="page-title">{title}</p>
    <p class="page-desc">{desc}</p>
  </div>
</div>
""", unsafe_allow_html=True)


def info_card(title: str, body: str):
    st.markdown(f"""
<div class="card">
  <div class="card-title">{title}</div>
  <div class="card-body">{body}</div>
</div>
""", unsafe_allow_html=True)


def badge(text: str, color: str = "blue"):
    st.markdown(f'<span class="badge badge-{color}">{text}</span>', unsafe_allow_html=True)
