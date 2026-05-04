"""
異常検知ロジック（ツール⑤共通）
"""
import pandas as pd
import numpy as np


def detect_anomalies(df: pd.DataFrame, value_col: str, date_col: str) -> pd.DataFrame:
    df = df.copy().sort_values(date_col).reset_index(drop=True)
    df[date_col] = pd.to_datetime(df[date_col])
    df["rolling_mean"] = df[value_col].rolling(window=7, min_periods=1).mean()
    df["rolling_std"]  = df[value_col].rolling(window=7, min_periods=1).std().fillna(0)
    df["z_score"]      = (df[value_col] - df["rolling_mean"]) / (df["rolling_std"] + 1e-9)
    df["is_anomaly"]   = df["z_score"].abs() > 2.0
    df["pct_change"]   = df[value_col].pct_change().fillna(0) * 100
    return df


def build_anomaly_summary(df: pd.DataFrame, value_col: str, date_col: str) -> str:
    anomalies = df[df["is_anomaly"]]
    lines = [
        f"分析期間: {df[date_col].min().date()} 〜 {df[date_col].max().date()}",
        f"総データ点数: {len(df)}",
        f"異常検知数: {len(anomalies)}",
        f"平均値: {df[value_col].mean():.2f}",
        f"最大値: {df[value_col].max():.2f}（{df.loc[df[value_col].idxmax(), date_col].date()}）",
        f"最小値: {df[value_col].min():.2f}（{df.loc[df[value_col].idxmin(), date_col].date()}）",
    ]
    if not anomalies.empty:
        lines.append("\n## 検知された異常")
        for _, row in anomalies.iterrows():
            direction = "急騰" if row["z_score"] > 0 else "急落"
            lines.append(
                f"- {row[date_col].date()} : {direction}"
                f"（値={row[value_col]:.2f}, 変化率={row['pct_change']:+.1f}%, Z={row['z_score']:.2f}）"
            )
    return "\n".join(lines)
