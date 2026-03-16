"""精神搭子 Agent — Groq LLM 情绪陪伴对话引擎"""

import json
import re

from openai import OpenAI

import config
import mood_diary

# ── Groq Client ──────────────────────────────────────────
_client: OpenAI | None = None

def _get_client() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI(api_key=config.GROQ_API_KEY, base_url=config.GROQ_BASE_URL)
    return _client


# ── System Prompt ────────────────────────────────────────
SYSTEM_PROMPT = """你是"搭子"——一个温柔、站队、不说教的情绪陪伴搭子。

## 你的核心原则
1. **永远站用户这边**，先接住情绪，再做其他事
2. **不说教、不评判**，少用"你应该/你必须"
3. **用选择题交还控制权**，不替用户做决定
4. **保持温柔直白**，少术语、少鸡汤
5. 遇到自伤/极端风险时，温柔建议寻求专业帮助

## 你的话术模板
用"3句理解 + 1句轻建议"：
1）"我听见你在……（复述感受）"
2）"换成谁都会……（归因正常化）"
3）"你其实已经……（肯定努力）"
4）"要不要试试：A / B / C（轻建议，给选择）"

## 你的口头禅
- "我懂，这事真离谱。"
- "你已经做得很好了。"
- "我们先把你接住，再看下一步。"

## 对话模式自动路由
- 用户说"累/烦/无语/不想干了/崩溃" → **吐槽模式**：先共情，不提建议，复述总结，给选择（继续骂/安慰/分析）
- 用户说"怎么做/帮我看看/给建议" → **分析模式**：先问目标，再给3个选项
- 用户说"记录/打卡/今天心情" → **打卡模式**：询问心情分数+关键词
- 其他 → 日常闲聊，保持温柔陪伴

## 可用工具
当需要记录或查询数据时，输出以下格式的 JSON 块：

### record_mood
记录用户的情绪日记。在对话中自然收集到心情信息后调用。
参数:
- mood_score (int, 1-10): 心情分数
- keywords (list[str]): 3-5个情绪关键词
- tags (list[str]): 分类标签（工作/关系/身体/家庭/自我价值/其他）
- summary (str): 一句话摘要
- trigger (str, 可选): 触发场景
- relief_action (str, 可选): 缓解行为

### get_weekly_report
获取每周情绪小结。
参数:
- weeks_ago (int, 默认0): 0=本周, 1=上周

### get_today_entries
获取今天的情绪记录。无参数。

## 调用格式
```tool_call
{"tool": "工具名", "params": {参数}}
```

## 重要规则
1. 不要在每次对话都强制记录，自然聊天中感觉到情绪节点时再提议记录
2. 记录前先询问用户"要不要我帮你记下今天的心情？"，得到同意再调用工具
3. 周报请求时直接调用 get_weekly_report 并用温柔的语言总结
4. 回复使用中文，保持口语化、亲切感
"""


# ── 工具映射 ─────────────────────────────────────────────
def _tool_record_mood(params: dict) -> dict:
    entry = mood_diary.add_entry(**params)
    return {"success": True, "entry": entry}

def _tool_weekly_report(params: dict) -> dict:
    report = mood_diary.weekly_report(params.get("weeks_ago", 0))
    return {"success": True, "report": report}

def _tool_today_entries(params: dict) -> dict:
    entries = mood_diary.get_today()
    return {"success": True, "entries": entries, "count": len(entries)}

TOOL_MAP = {
    "record_mood": _tool_record_mood,
    "get_weekly_report": _tool_weekly_report,
    "get_today_entries": _tool_today_entries,
}


# ── 解析与执行 ───────────────────────────────────────────
_TOOL_RE = re.compile(r"```tool_call\s*\n(.*?)\n```", re.DOTALL)

def _parse_tool_calls(text: str) -> list[dict]:
    calls = []
    for m in _TOOL_RE.finditer(text):
        try:
            calls.append(json.loads(m.group(1)))
        except json.JSONDecodeError:
            pass
    return calls

def _execute_tool(call: dict) -> dict:
    name = call.get("tool", "")
    params = call.get("params", {})
    fn = TOOL_MAP.get(name)
    if not fn:
        return {"success": False, "error": f"未知工具: {name}"}
    try:
        return fn(params)
    except Exception as e:
        return {"success": False, "error": str(e)}


# ── Chat 主函数 ──────────────────────────────────────────
def chat(user_message: str, conversation_history: list[dict]) -> dict:
    """处理用户消息，返回 {"reply": str, "tool_calls": list, "mood_recorded": bool}"""
    conversation_history.append({"role": "user", "content": user_message})

    messages = [{"role": "system", "content": SYSTEM_PROMPT}] + conversation_history

    all_tool_calls = []
    mood_recorded = False

    for _ in range(3):
        resp = _get_client().chat.completions.create(
            model=config.AI_MODEL,
            messages=messages,
            temperature=0.7,
            max_tokens=1024,
        )
        reply = resp.choices[0].message.content or ""
        tool_calls = _parse_tool_calls(reply)

        if not tool_calls:
            clean = _TOOL_RE.sub("", reply).strip()
            conversation_history.append({"role": "assistant", "content": clean})
            return {"reply": clean, "tool_calls": all_tool_calls, "mood_recorded": mood_recorded}

        results_text = []
        for tc in tool_calls:
            result = _execute_tool(tc)
            all_tool_calls.append(tc)
            if tc.get("tool") == "record_mood" and result.get("success"):
                mood_recorded = True
            results_text.append(f"工具 {tc.get('tool')} 返回:\n{json.dumps(result, ensure_ascii=False)}")

        messages.append({"role": "assistant", "content": reply})
        messages.append({"role": "user", "content": "工具执行结果:\n" + "\n\n".join(results_text) + "\n\n请根据结果用温柔的语气回复用户。"})

    conversation_history.append({"role": "assistant", "content": reply})
    return {"reply": reply, "tool_calls": all_tool_calls, "mood_recorded": mood_recorded}
