"""
ツール①: 議事録 → アクションアイテム抽出Bot
"""

import streamlit as st
import pandas as pd
import sys, os

sys.path.append(os.path.join(os.path.dirname(__file__), "../.."))

from src.common.llm import chat_json
from src.common.ui import page_header, info_card
from src.common.file_utils import df_to_csv_bytes


def render():
    page_header(
        "🎙️",
        "議事録 → アクションアイテム抽出Bot",
        "議事録を貼り付けるだけで担当・タスク・期限を自動整理します",
    )

    tab_text, tab_audio = st.tabs(["📝 テキスト入力", "🎧 音声入力"])
    minutes_text = ""

    with tab_text:
        minutes_text = st.text_area(
            "議事録をここに貼ってください",
            height=220,
            placeholder="例）\n田中：資料は来週月曜までに作ります\n佐藤：クライアントへの連絡は今週中に対応します...",
        )

    with tab_audio:
        audio_file = st.file_uploader(
            "音声ファイル（mp3 / wav / m4a）", type=["mp3", "wav", "m4a"]
        )
        if audio_file:
            st.audio(audio_file)
            if st.button("🔤 文字起こし（Whisper）"):
                with st.spinner("文字起こし中..."):
                    try:
                        import openai, tempfile

                        oa = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY", ""))
                        with tempfile.NamedTemporaryFile(
                            delete=False, suffix="." + audio_file.name.split(".")[-1]
                        ) as tmp:
                            tmp.write(audio_file.read())
                        with open(tmp.name, "rb") as f:
                            result = oa.audio.transcriptions.create(
                                model="whisper-1", file=f, language="ja"
                            )
                        st.session_state["transcribed_minutes"] = result.text
                        st.success("文字起こし完了！")
                    except Exception as e:
                        st.error(f"エラー: {e}")
            if "transcribed_minutes" in st.session_state:
                minutes_text = st.session_state["transcribed_minutes"]
                st.text_area("文字起こし結果", value=minutes_text, height=160)

    st.divider()
    final_text = minutes_text.strip()

    if st.button(
        "⚡ アクションアイテムを抽出する", type="primary", disabled=not final_text
    ):
        with st.spinner("Claude が解析中..."):
            data = chat_json(f"""
以下の議事録からアクションアイテムをすべて抽出し、JSON形式で出力してください。

## 出力形式（JSONのみ）
{{
  "summary": "会議全体の要約を3行程度で",
  "items": [
    {{
      "担当": "氏名",
      "タスク": "具体的な作業内容",
      "期限": "日付や期限（記載なければ「未定」）"
    }}
  ]
}}

## 議事録
{final_text}
""")

        items = data.get("items", [])
        summary = data.get("summary", "")

        st.success(f"✅ {len(items)} 件のアクションアイテムを抽出しました")

        if summary:
            st.markdown("### 📝 会議の要約")
            st.info(summary)

        st.markdown("### 📋 アクションアイテム一覧")
        if items:
            df = pd.DataFrame(items)
            st.dataframe(df, use_container_width=True)

            st.download_button(
                "📥 CSVでダウンロード",
                data=df_to_csv_bytes(df),
                file_name="action_items.csv",
                mime="text/csv",
            )
        else:
            st.warning("アクションアイテムが見つかりませんでした。")
