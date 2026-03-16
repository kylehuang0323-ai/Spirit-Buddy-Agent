"""情绪日记 — JSON 存储的情绪记录 CRUD + 周报聚合"""

import json
import os
from datetime import datetime, timedelta
from collections import Counter

import config

DIARY_FILE = os.path.join(config.DATA_DIR, "diary.json")


def _load() -> list[dict]:
    if os.path.exists(DIARY_FILE):
        with open(DIARY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def _save(entries: list[dict]):
    with open(DIARY_FILE, "w", encoding="utf-8") as f:
        json.dump(entries, f, ensure_ascii=False, indent=2)


def add_entry(
    mood_score: int,
    keywords: list[str],
    tags: list[str],
    summary: str,
    trigger: str = "",
    relief_action: str = "",
) -> dict:
    """新增一条情绪日记"""
    entry = {
        "id": datetime.now().strftime("%Y%m%d%H%M%S"),
        "date": datetime.now().strftime("%Y-%m-%d"),
        "time": datetime.now().strftime("%H:%M"),
        "mood_score": max(1, min(10, mood_score)),
        "keywords": keywords,
        "tags": tags,
        "summary": summary,
        "trigger": trigger,
        "relief_action": relief_action,
    }
    entries = _load()
    entries.append(entry)
    _save(entries)
    return entry


def get_today() -> list[dict]:
    """获取今天的日记"""
    today = datetime.now().strftime("%Y-%m-%d")
    return [e for e in _load() if e["date"] == today]


def get_recent(days: int = 7) -> list[dict]:
    """获取最近 N 天的日记"""
    cutoff = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    return [e for e in _load() if e["date"] >= cutoff]


def get_all() -> list[dict]:
    return _load()


def weekly_report(weeks_ago: int = 0) -> dict:
    """生成周报：趋势、高低点、触发模式、缓解方式排行

    weeks_ago=0 表示本周，1 表示上周
    """
    now = datetime.now()
    # 计算目标周的周一和周日
    start_of_week = now - timedelta(days=now.weekday() + 7 * weeks_ago)
    start_of_week = start_of_week.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_week = start_of_week + timedelta(days=6, hours=23, minutes=59)

    start_str = start_of_week.strftime("%Y-%m-%d")
    end_str = end_of_week.strftime("%Y-%m-%d")

    entries = [e for e in _load() if start_str <= e["date"] <= end_str]

    if not entries:
        return {
            "period": f"{start_str} ~ {end_str}",
            "total_entries": 0,
            "message": "这周还没有情绪记录哦，记得来和搭子聊聊～",
        }

    scores = [e["mood_score"] for e in entries]
    all_tags = [t for e in entries for t in e.get("tags", [])]
    all_keywords = [k for e in entries for k in e.get("keywords", [])]
    all_triggers = [e["trigger"] for e in entries if e.get("trigger")]
    all_reliefs = [e["relief_action"] for e in entries if e.get("relief_action")]

    # 找最高分和最低分那天
    best = max(entries, key=lambda e: e["mood_score"])
    worst = min(entries, key=lambda e: e["mood_score"])

    return {
        "period": f"{start_str} ~ {end_str}",
        "total_entries": len(entries),
        "avg_score": round(sum(scores) / len(scores), 1),
        "highest": {"date": best["date"], "score": best["mood_score"], "summary": best["summary"]},
        "lowest": {"date": worst["date"], "score": worst["mood_score"], "summary": worst["summary"]},
        "score_trend": [{"date": e["date"], "score": e["mood_score"]} for e in entries],
        "top_tags": Counter(all_tags).most_common(5),
        "top_keywords": Counter(all_keywords).most_common(5),
        "top_triggers": Counter(all_triggers).most_common(3),
        "top_reliefs": Counter(all_reliefs).most_common(3),
    }
