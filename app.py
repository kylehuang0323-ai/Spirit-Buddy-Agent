"""精神搭子 — Flask 主应用"""

import os
import json
from flask import Flask, render_template, request, jsonify

import config
import agent
import mood_diary

app = Flask(__name__)
app.secret_key = config.SECRET_KEY

_chat_history: list[dict] = []


@app.route("/")
def index():
    return render_template("chat.html")


@app.route("/diary")
def diary_page():
    return render_template("diary.html")


@app.route("/api/chat", methods=["POST"])
def api_chat():
    data = request.get_json(force=True)
    msg = data.get("message", "").strip()
    if not msg:
        return jsonify({"error": "message is required"}), 400
    result = agent.chat(msg, _chat_history)
    return jsonify(result)


@app.route("/api/chat/clear", methods=["POST"])
def api_chat_clear():
    _chat_history.clear()
    return jsonify({"status": "ok"})


@app.route("/api/diary/today")
def api_diary_today():
    return jsonify({"entries": mood_diary.get_today()})


@app.route("/api/diary/recent")
def api_diary_recent():
    days = request.args.get("days", 7, type=int)
    return jsonify({"entries": mood_diary.get_recent(days)})


@app.route("/api/diary/weekly-report")
def api_weekly_report():
    weeks_ago = request.args.get("weeks_ago", 0, type=int)
    return jsonify(mood_diary.weekly_report(weeks_ago))


@app.route("/api/diary/record", methods=["POST"])
def api_diary_record():
    data = request.get_json(force=True)
    entry = mood_diary.add_entry(
        mood_score=data.get("mood_score", 5),
        keywords=data.get("keywords", []),
        tags=data.get("tags", []),
        summary=data.get("summary", ""),
        trigger=data.get("trigger", ""),
        relief_action=data.get("relief_action", ""),
    )
    return jsonify({"success": True, "entry": entry})


if __name__ == "__main__":
    print("=" * 40)
    print("🧸 精神搭子 — 你的情绪陪伴搭子")
    print("🌐 http://localhost:5002")
    print("=" * 40)
    app.run(debug=True, host="127.0.0.1", port=5002)
