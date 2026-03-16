# 🧸 精神搭子 — Spirit Buddy

> 一个温柔站队、不说教的情绪陪伴型 AI Agent

精神搭子是一款基于 Groq LLM（Llama 3.3-70B）的私人情绪陪伴工具，结合实时对话、心情打卡和数据可视化，帮助你在日常中获得温暖的情绪支持。

![Python](https://img.shields.io/badge/Python-3.7+-blue?logo=python)
![Flask](https://img.shields.io/badge/Flask-3.0+-green?logo=flask)
![Groq](https://img.shields.io/badge/LLM-Groq%20Llama%203.3--70B-orange)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## ✨ 功能亮点

| 功能 | 说明 |
|------|------|
| 💬 **智能对话** | 三段式共情回复：复述感受 → 正常化 → 肯定努力 + 轻量建议 |
| 🔀 **自动路由** | 根据语境自动切换：吐槽模式 / 分析模式 / 打卡模式 / 闲聊模式 |
| 📝 **心情打卡** | Agent 自主记录心情分数(1-10)、关键词、标签、触发事件、缓解方式 |
| 📊 **周报分析** | 情绪趋势折线图 + 高频标签 + 最有效缓解方式排行 |
| 🔧 **Tool Calling** | Agent 可自主调用工具：记录心情、查询周报、获取今日记录 |
| 🔒 **本地存储** | JSON 文件存储，数据完全留在本地，保护隐私 |

---

## 🖼️ 界面预览

### 对话界面 (`/`)
紫色渐变 + 玻璃拟态风格的沉浸式聊天界面，支持实时对话和心情记录提示。

### 周报页面 (`/diary`)
Chart.js 情绪趋势图 + 统计卡片 + 近期心情条目列表。

---

## 🏗️ 项目结构

```
精神搭子/
├── agent.py              # LLM Agent 核心（人设 + 工具 + 路由）
├── mood_diary.py         # 心情日记数据模型 & 周报分析
├── app.py                # Flask 应用 & API 路由
├── config.py             # 配置（Groq API、模型、密钥）
├── requirements.txt      # 依赖
├── .env                  # 环境变量（API Key）
├── data/
│   └── diary.json        # 心情记录存储
├── static/
│   └── style.css         # 聊天界面样式
└── templates/
    ├── chat.html         # 主聊天页面
    └── diary.html        # 周报分析页面
```

---

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置 API Key

创建 `.env` 文件：

```env
GROQ_API_KEY=your_groq_api_key_here
```

> 💡 在 [Groq Console](https://console.groq.com/) 免费获取 API Key

### 3. 启动应用

```bash
python app.py
```

访问 **http://localhost:5002** 开始聊天 🎉

---

## 📡 API 接口

### 对话

| 路由 | 方法 | 说明 |
|------|------|------|
| `/api/chat` | POST | 发送消息，返回 AI 回复 |
| `/api/chat/clear` | POST | 清空对话历史 |

### 心情日记

| 路由 | 方法 | 说明 |
|------|------|------|
| `/api/diary/today` | GET | 获取今日记录 |
| `/api/diary/recent?days=7` | GET | 获取近 N 天记录 |
| `/api/diary/weekly-report?weeks_ago=0` | GET | 获取周报（0=本周） |
| `/api/diary/record` | POST | 手动添加心情记录 |

### 页面

| 路由 | 说明 |
|------|------|
| `/` | 聊天主页 |
| `/diary` | 心情周报 |

---

## 🤖 Agent 设计

### 人设原则

- **温柔站队**：永远先认同用户的感受
- **不说教**：不评判、不讲大道理
- **归还主动权**：用选项让用户自己决定下一步
- **安全底线**：识别到自伤风险时温和引导专业求助

### 回复模板

```
1. 复述感受：「我听到你说……」
2. 正常化：「换谁都会……」
3. 肯定努力：「你已经在……」
4. 轻量建议：「要不要试试 A / B / C？」
```

### 工具列表

| 工具 | 说明 |
|------|------|
| `record_mood` | 记录心情（分数 + 关键词 + 标签 + 触发事件 + 缓解方式） |
| `get_weekly_report` | 获取周报摘要 |
| `get_today_entries` | 获取今日所有记录 |

---

## 🎨 技术栈

| 层 | 技术 |
|----|------|
| **后端** | Flask 3.0+ |
| **LLM** | Groq API — Llama 3.3-70B-Versatile (temperature=0.7) |
| **LLM Client** | OpenAI Python SDK |
| **前端** | HTML5 + Vanilla JS + Bootstrap 5.3 |
| **图表** | Chart.js 4 |
| **数据存储** | JSON 文件 |
| **环境** | python-dotenv |

---

## 📊 心情数据格式

每条记录存储为：

```json
{
  "id": "20250316143025",
  "date": "2025-03-16",
  "time": "14:30",
  "mood_score": 7,
  "keywords": ["疲惫", "满足"],
  "tags": ["工作", "自我价值"],
  "summary": "完成了项目，虽然累但值得",
  "trigger": "项目 deadline",
  "relief_action": "喝咖啡休息30分钟"
}
```

---

## 📝 开发说明

- **端口**：默认 5002（可在 `app.py` 修改）
- **对话历史**：保存在内存中，重启后清空
- **日记数据**：持久化在 `data/diary.json`
- **模型温度**：0.7（比常规 Agent 高，让回复更自然多变）

---

## 📄 License

MIT License — 自由使用，记得给 ⭐ 

---

> *「你不需要变好才值得被倾听。」* — 🧸 精神搭子
