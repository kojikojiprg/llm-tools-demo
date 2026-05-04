"""
ツール④: GA4 × Slack 週次レポート自動送信
"""

import streamlit as st
import os, sys

sys.path.append(os.path.join(os.path.dirname(__file__), "../.."))

from src.common.llm import chat_json
from src.common.ui import page_header, info_card


def _fetch_ga4_data(property_id: str) -> dict:
    from google.analytics.data_v1beta import BetaAnalyticsDataClient
    from google.analytics.data_v1beta.types import (
        RunReportRequest,
        DateRange,
        Metric,
        Dimension,
    )
    from datetime import date, timedelta

    ga = BetaAnalyticsDataClient()
    today = date.today()
    last_week = today - timedelta(days=7)
    prev_week = today - timedelta(days=14)

    def run(start, end):
        return ga.run_report(
            RunReportRequest(
                property=f"properties/{property_id}",
                date_ranges=[
                    DateRange(start_date=start.isoformat(), end_date=end.isoformat())
                ],
                metrics=[
                    Metric(name="sessions"),
                    Metric(name="activeUsers"),
                    Metric(name="bounceRate"),
                    Metric(name="averageSessionDuration"),
                ],
                dimensions=[Dimension(name="date")],
            )
        )

    def total(report, idx):
        return sum(float(r.metric_values[idx].value) for r in report.rows)

    cur = run(last_week, today)
    prv = run(prev_week, last_week)
    return {
        "期間": f"{last_week} 〜 {today}",
        "セッション数": int(total(cur, 0)),
        "セッション数_前週": int(total(prv, 0)),
        "ユーザー数": int(total(cur, 1)),
        "直帰率": round(total(cur, 2) / max(len(cur.rows), 1), 3),
        "平均セッション時間": round(total(cur, 3) / max(len(cur.rows), 1), 1),
    }


def _post_slack(channel_id: str, token: str, text: str):
    from slack_sdk import WebClient

    WebClient(token=token).chat_postMessage(channel=channel_id, text=text, mrkdwn=True)


def render():
    page_header(
        "📈",
        "GA4 × Slack 週次レポート",
        "GA4データを取得してAIコメント付きレポートをSlackに自動投稿します",
    )

    st.markdown("### ⚙️ 設定")
    property_id = st.text_input(
        "GA4 プロパティID",
        value=os.environ.get("GA4_PROPERTY_ID", ""),
        placeholder="123456789",
    )
    slack_token = st.text_input(
        "Slack Bot Token", value=os.environ.get("SLACK_BOT_TOKEN", ""), type="password"
    )
    channel_id = st.text_input(
        "Slack チャンネルID",
        value=os.environ.get("SLACK_CHANNEL_ID", ""),
        placeholder="C0XXXXXXXXX",
    )

    st.divider()
    info_card(
        "📋 事前準備",
        "① Google Cloud でサービスアカウントを作成し <code>service_account.json</code> を保存<br>"
        "② GA4 管理画面でサービスアカウントに「閲覧者」権限を付与<br>"
        "③ Slack App を作成し <code>chat:write</code> 権限を付与してBotをチャンネルに招待",
    )

    if st.button(
        "⚡ 今すぐレポートを送信",
        type="primary",
        disabled=not all([property_id, slack_token, channel_id]),
    ):
        with st.spinner("GA4からデータ取得中..."):
            try:
                ga_data = _fetch_ga4_data(property_id)
            except Exception as e:
                st.error(f"GA4取得エラー: {e}")
                return

        with st.spinner("AIコメント生成中..."):
            import json

            insight = chat_json(f"""
以下はWebサイトの先週のGA4データです。マーケター向けに週次コメントをJSON形式で返してください。

## 出力形式（JSONのみ）
{{
  "総評": "2〜3行の全体コメント",
  "良かった点": ["ポイント1", "ポイント2"],
  "改善ポイント": ["ポイント1", "ポイント2"],
  "来週のアクション": ["アクション1"]
}}

## GA4データ
{json.dumps(ga_data, ensure_ascii=False, indent=2)}
""")

        diff = ga_data["セッション数"] - ga_data["セッション数_前週"]
        sign = "📈" if diff >= 0 else "📉"
        text = f"""
*📊 週次サイトレポート｜{ga_data['期間']}*

{sign} セッション数：*{ga_data['セッション数']:,}*（前週比 {diff:+,}）
👥 ユーザー数：*{ga_data['ユーザー数']:,}*
⏱ 平均滞在：*{ga_data['平均セッション時間']:.0f}秒*　直帰率：*{ga_data['直帰率']:.1%}*

*🧠 AIコメント*
{insight['総評']}

✅ *良かった点*
{chr(10).join(f'• {p}' for p in insight['良かった点'])}

⚠️ *改善ポイント*
{chr(10).join(f'• {p}' for p in insight['改善ポイント'])}

🎯 *来週のアクション*
{chr(10).join(f'• {a}' for a in insight['来週のアクション'])}
""".strip()

        with st.spinner("Slackに投稿中..."):
            try:
                _post_slack(channel_id, slack_token, text)
                st.success("✅ Slackに投稿しました！")
            except Exception as e:
                st.error(f"Slack投稿エラー: {e}")

        st.markdown("### 📋 投稿内容プレビュー")
        st.code(text, language="markdown")
