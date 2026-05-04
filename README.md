# 🤖 AI Tools Suite

Python × Claude API × データ分析で作る6つのビジネスツール集。

## 🗂 ディレクトリ構成

```
ai-tools-suite/
├── app.py                        # メインアプリ（エントリーポイント）
└── src
│   ├── common
│   │   ├── file_utils.py         # PDF・CSV読み込み共通処理
│   │   ├── llm.py                # Claude API 共通クライアント
│   │   └── ui.py                 # スタイル・UIヘルパー
│   └── tools
│       ├── anomaly_detection
│       │   ├── detector.py       # 異常検知ロジック
│       │   └── tool.py           # ⑤ 異常検知Bot UI
│       ├── contract_bot
│       │   └── tool.py           # ② 契約書Bot
│       ├── csv_analysis
│       │   └── tool.py           # ③ CSV分析Bot
│       ├── ga4_slack
│       │   └── tool.py           # ④ GA4×Slackレポート
│       ├── minutes_bot
│       │   └── tool.py           # ① 議事録Bot
│       └── rag_system
│           ├── rag.py            # RAGロジック（インデックス・検索）
│           └── tool.py           # ⑥ RAGシステム UI
├── requirements.txt
├── .env
└── .gitignore
```

## 🚀 セットアップ

```bash
# 1. 仮想環境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. パッケージ
pip install -r requirements.txt

# 3. 環境変数
cp .env.example .env
# .env を編集して ANTHROPIC_API_KEY を設定

# 4. 起動
streamlit run app.py
```

## 🛠 ツール一覧

| # | ツール | 必要なAPIキー |
|---|-------|-------------|
| ① | 議事録Bot | ANTHROPIC_API_KEY |
| ② | 契約書Bot | ANTHROPIC_API_KEY |
| ③ | CSV分析Bot | ANTHROPIC_API_KEY |
| ④ | GA4×Slackレポート | ANTHROPIC + GA4 + Slack |
| ⑤ | 異常検知Bot | ANTHROPIC_API_KEY |
| ⑥ | RAGシステム | ANTHROPIC_API_KEY |

## 📦 共通モジュール

| モジュール | 役割 |
|-----------|------|
| `common/llm.py` | `chat()` / `chat_json()` で全ツール共通のAPI呼び出し |
| `common/file_utils.py` | PDF・CSVの読み込み・チャンク分割 |
| `common/ui.py` | ページヘッダー・カード・バッジ等のUIヘルパー |
