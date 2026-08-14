import os
from openai import AsyncOpenAI
from models import AgentState

# 使用 SiliconFlow 提供的模型服务
client = AsyncOpenAI(
    api_key=os.getenv("LLM_API_KEY", "your-api-key"),
    base_url=os.getenv("LLM_BASE_URL", "https://api.siliconflow.cn/v1")
)
# 默认使用 Qwen2.5-7B-Instruct
MODEL = os.getenv("LLM_MODEL", "Qwen/Qwen2.5-7B-Instruct")

async def call_llm(system_prompt: str, user_prompt: str) -> str:
    """封装对大模型的调用"""
    resp = await client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.7,
        max_tokens=2048
    )
    return resp.choices[0].message.content


async def product_manager_agent(state: AgentState) -> AgentState:
    """
    产品经理节点：将一句话需求转化为 PRD。
    """
    system_prompt = (
        "你是一位资深产品经理(PM)。"
        "你需要将用户的简单需求，扩展为一个结构清晰的产品需求文档(PRD)。"
        "PRD需要包括：1. 核心功能 2. 交互逻辑 3. 约束条件。"
        "请直接输出 Markdown 格式的 PRD，不要有多余的寒暄。"
    )
    user_prompt = f"用户的需求是：{state.task}"
    
    prd = await call_llm(system_prompt, user_prompt)
    
    # 更新状态
    state.prd = prd
    state.status = "PRD_DONE"
    state.history.append({"agent": "PM", "content": "PRD 已生成"})
    return state


async def developer_agent(state: AgentState) -> AgentState:
    """
    程序员节点：根据 PRD 编写代码。
    """
    system_prompt = (
        "你是一位资深 Python 程序员。"
        "你需要严格按照产品经理的 PRD 编写完整、可运行的代码，并处理审查员(如果有)给出的 Feedback。"
        "【极其重要】你必须且只能输出包含 Python 代码的 Markdown 代码块，例如：\n"
        "```python\n"
        "这里写代码\n"
        "```\n"
        "代码需要是完整的、可以直接运行的（例如贪吃蛇游戏需要完整的 pygame 或 curses 实现）。"
        "不要包含任何解释性文字，不要寒暄！"
    )
    
    user_prompt = f"以下是 PRD：\n{state.prd}\n"
    if state.feedback:
        user_prompt += f"\n这是 Reviewer 的修改意见，请必须根据意见修复代码：\n{state.feedback}"
        
    code_text = await call_llm(system_prompt, user_prompt)
    
    # 更健壮地提取代码块
    import re
    code = code_text
    # 尝试匹配 ```python ... ``` 或者 ``` ... ```
    match = re.search(r"```(?:python)?\s*(.*?)\s*```", code_text, re.DOTALL | re.IGNORECASE)
    if match:
        code = match.group(1).strip()
    else:
        # 如果大模型完全没有输出代码块，可能全篇都是代码或者混杂了文字，去除首尾空白
        code = code_text.strip()
        
    # 如果提取出的代码依然为空，给个保底的注释防止后续报错
    if not code:
        code = "# 大模型未能生成有效代码，请检查模型能力或 Prompt。"
        
    # 更新状态
    state.code = code
    state.status = "CODE_DONE"
    state.history.append({"agent": "Coder", "content": "代码已生成/修改"})
    return state


async def reviewer_agent(state: AgentState) -> AgentState:
    """
    代码审查节点：检查代码逻辑，决定通过还是打回。
    """
    system_prompt = (
        "你是一位代码审查员。"
        "请检查代码是否能正常运行且满足需求。"
        "回复格式必须严格遵守，只能是以下两种之一："
        "1. 如果代码没有明显bug且能运行：第一行只写 APPROVED，不要写其他任何内容。"
        "2. 如果代码有明显bug：第一行写 REJECTED，第二行开始写具体问题。"
        "注意：第一行必须只有 APPROVED 或 REJECTED 这一个单词，不能有其他文字。"
    )
    
    user_prompt = f"PRD：\n{state.prd}\n\n程序员提交的代码：\n{state.code}"
    
    review_result = await call_llm(system_prompt, user_prompt)
    
    first_line = review_result.strip().split("\n")[0].strip().upper()
    if "APPROVED" in first_line:
        state.status = "APPROVED"
        state.feedback = ""
        state.history.append({"agent": "Reviewer", "content": "代码审查通过 ✅"})
    else:
        state.status = "REJECTED"
        # 提取 REJECTED 之后的文字作为 Feedback
        feedback = review_result.replace("REJECTED", "").strip()
        state.feedback = feedback
        state.history.append({"agent": "Reviewer", "content": f"打回重做 ❌ 意见：{feedback}"})
        
    return state




