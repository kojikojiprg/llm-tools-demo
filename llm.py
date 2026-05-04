"""
共通モジュール: Claude APIクライアント
"""
import os
import json
import anthropic
from dotenv import load_dotenv

load_dotenv()

_client: anthropic.Anthropic | None = None


def get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY が .env に設定されていません")
        _client = anthropic.Anthropic(api_key=api_key)
    return _client


def chat(prompt: str, max_tokens: int = 2048, system: str | None = None) -> str:
    """シンプルな1ターン会話。テキストを返す。"""
    client = get_client()
    kwargs = dict(
        model="claude-sonnet-4-20250514",
        max_tokens=max_tokens,
        messages=[{"role": "user", "content": prompt}],
    )
    if system:
        kwargs["system"] = system
    message = client.messages.create(**kwargs)
    return message.content[0].text


def chat_json(prompt: str, max_tokens: int = 2048) -> dict:
    """JSONを返すことを期待する会話。パース済みdictを返す。"""
    raw = chat(prompt, max_tokens=max_tokens)
    raw = raw.strip()
    try:
        start = raw.index("{")
        end = raw.rindex("}") + 1
        return json.loads(raw[start:end])
    except Exception as e:
        raise ValueError(f"JSONパース失敗:\n{raw}") from e
