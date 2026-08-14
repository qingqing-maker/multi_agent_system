from typing import Callable, Dict, Any, Awaitable
from models import AgentState
import logging

logger = logging.getLogger("Graph")

class StateGraph:
    """
    手写的轻量级状态图引擎 (灵感来自 LangGraph)
    负责 Agent 节点的注册以及根据条件进行节点跳转。
    """
    def __init__(self):
        self.nodes: Dict[str, Callable[[AgentState], Awaitable[AgentState]]] = {}
        self.entry_point: str = None
        self.edges: Dict[str, Callable[[AgentState], str]] = {}
        
    def add_node(self, name: str, action: Callable[[AgentState], Awaitable[AgentState]]):
        """添加一个处理节点 (Agent)"""
        self.nodes[name] = action
        
    def set_entry_point(self, name: str):
        """设置图的入口节点"""
        self.entry_point = name
        
    def add_conditional_edges(self, source: str, condition: Callable[[AgentState], str]):
        """
        添加条件边：
        当 source 节点执行完毕后，执行 condition 函数，
        condition 函数的返回值就是下一个要执行的节点名字。如果返回 'END' 则结束。
        """
        self.edges[source] = condition
        
    async def run(self, initial_state: AgentState, max_steps: int = 10) -> AgentState:
        """运行图引擎"""
        current_node = self.entry_point
        state = initial_state
        step = 0
        
        while current_node != "END" and step < max_steps:
            logger.info(f"\n--- [执行节点: {current_node}] ---")
            
            # 获取当前节点对应的 Agent 函数
            action = self.nodes.get(current_node)
            if not action:
                raise ValueError(f"找不到节点: {current_node}")
                
            # 执行 Agent 函数，更新状态
            state = await action(state)
            
            # 决定下一步去哪
            if current_node in self.edges:
                condition_func = self.edges[current_node]
                next_node = condition_func(state)
                current_node = next_node
            else:
                current_node = "END" # 没有定义边就默认结束
                
            step += 1
            
        if step >= max_steps:
            logger.warning("达到最大执行步数，图引擎强制终止。")
            
        return state
