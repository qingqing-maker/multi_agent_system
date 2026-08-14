import os
import asyncio
import logging
from dotenv import load_dotenv

# 必须在 import agents 之前调用！agents.py 模块加载时就会创建 AsyncOpenAI client
load_dotenv()

from models import AgentState
from agents import product_manager_agent, developer_agent, reviewer_agent
from graph import StateGraph

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

async def main():
    import sys
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    print("🚀 自动化软件开发流水线启动！\n")
    
    if len(sys.argv) > 1:
        user_task = " ".join(sys.argv[1:])
    else:
        user_task = "写一个用 Python 打印九九乘法表的脚本"
        
    print(f"当前需求：{user_task}\n")
    
    # 1. 初始化全局状态
    initial_state = AgentState(task=user_task)
    
    # 2. 构建图引擎
    workflow = StateGraph()
    
    # 注册节点
    workflow.add_node("PM", product_manager_agent)
    workflow.add_node("Coder", developer_agent)
    workflow.add_node("Reviewer", reviewer_agent)
    
    # 设置入口
    workflow.set_entry_point("PM")
    
    # 3. 定义图的路由逻辑 (Edges)
    # PM 搞完给 Coder
    workflow.add_conditional_edges(
        "PM", 
        lambda state: "Coder" if state.status == "PRD_DONE" else "END"
    )
    
    # Coder 搞完给 Reviewer
    workflow.add_conditional_edges(
        "Coder",
        lambda state: "Reviewer" if state.status == "CODE_DONE" else "END"
    )
    
    # ⭐️ 核心循环机制：Reviewer 决定是结束还是重写
    workflow.add_conditional_edges(
        "Reviewer",
        lambda state: "END" if state.status == "APPROVED" else "Coder"
    )
    
    # 4. 执行图引擎（最多3轮审查）
    final_state = await workflow.run(initial_state, max_steps=8)
    
    # 5. 输出结果
    print("\n================ 🏆 最终产出 ================")
    print(f"\n[产品需求文档 PRD]:\n{final_state.prd}")
    print(f"\n[最终源代码 CODE]:\n```python\n{final_state.code}\n```")
    
    # 自动将代码保存为文件
    with open("output_app.py", "w", encoding="utf-8") as f:
        f.write(final_state.code)
    print("\n✅ 代码已自动保存到当前目录的 output_app.py 中！您可以直接运行它。")

if __name__ == "__main__":
    # Windows 下可能需要设置 SelectorEventLoop 以避免某些环境下的报错
    import sys
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())


