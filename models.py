from pydantic import BaseModel, Field
from typing import Optional, List

class AgentState(BaseModel):
    """
    多 Agent 系统中的全局状态 (State)。
    相当于在团队中流转的同一个"项目文件夹"。
    """
    # 用户的原始需求
    task: str
    
    # 历史对话记录，用于在 Agent 间共享上下文
    history: List[dict] = Field(default_factory=list)
    
    # 产出物
    prd: Optional[str] = None       # 产品经理写的 PRD
    code: Optional[str] = None      # 程序员写的代码
    feedback: Optional[str] = None  # 审查员的代码反馈
    
    # 当前状态流转控制
    status: str = "INIT"            # INIT / PRD_DONE / CODE_DONE / APPROVED / REJECTED
