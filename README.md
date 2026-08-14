# Multi-Agent 自动化软件开发流水线

这是一个使用 Python 实现的轻量级多 Agent 协作示例。用户输入一句软件需求后，系统会让多个由大语言模型驱动的 Agent 按照固定流程协作：

```text
用户需求
  → 产品经理（PM）生成 PRD
  → 程序员（Coder）生成 Python 代码
  → 审查员（Reviewer）审核代码
      ├─ APPROVED：结束并保存代码
      └─ REJECTED：携带审核意见返回程序员修改
```

项目没有直接依赖 LangGraph，而是在 `graph.py` 中实现了一个简化的异步状态图，适合用于学习多 Agent 工作流、状态流转和大模型 API 调用。

## Pygame 贪吃蛇游戏在哪里

当前生成的贪吃蛇游戏位于：

```text
E:\project-qing\multi_agent_system\output_app.py
```

`output_app.py` 是多 Agent 流水线生成的产物，不是流水线的核心源码。再次运行 `main.py` 生成其他程序时，这个文件会被直接覆盖。

## 快速运行贪吃蛇

### 方式一：使用项目现有虚拟环境

当前项目的 `.venv` 已安装 Pygame，可以在 PowerShell 或 CMD 中执行：

```powershell
cd "E:\project-qing\multi_agent_system"
.\.venv\Scripts\python.exe .\output_app.py
```

在 Git Bash 中执行：

```bash
cd /e/project-qing/multi_agent_system
./.venv/Scripts/python.exe output_app.py
```

### 方式二：创建新的虚拟环境

如果现有 `.venv` 不可用，建议重新创建虚拟环境：

```powershell
cd "E:\project-qing\multi_agent_system"
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install pygame
.\.venv\Scripts\python.exe .\output_app.py
```

> `requirements.txt` 当前记录的是多 Agent 流水线自身的依赖，并未包含生成程序所需的 `pygame`，因此运行贪吃蛇前需要确保 Pygame 已安装。

### 游戏操作

| 按键 | 功能 |
|---|---|
| 任意键 | 在开始界面进入游戏 |
| `↑` `↓` `←` `→` | 控制蛇的移动方向 |
| `Space` | 暂停或继续 |
| `R`、`Space` 或 `Enter` | 游戏结束后重新开始 |
| `Esc` | 退出游戏 |

最高分会保存在运行目录下的 `highscore.txt` 中。

## 运行环境

推荐环境：

- Windows 10/11
- Python 3.10 或更高版本
- 可访问的 OpenAI Chat Completions 兼容 API

当前项目虚拟环境使用 Python 3.12。

## 安装多 Agent 流水线依赖

在 PowerShell 或 CMD 中执行：

```powershell
cd "E:\project-qing\multi_agent_system"
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

如果还要运行当前的贪吃蛇产物，请额外安装 Pygame：

```powershell
.\.venv\Scripts\python.exe -m pip install pygame
```

项目自身依赖如下：

| 依赖 | 用途 |
|---|---|
| `openai` | 调用 OpenAI 兼容的大模型 API |
| `pydantic` | 定义 Agent 之间共享的状态模型 |
| `python-dotenv` | 从 `.env` 加载环境变量 |

## 配置大模型

在项目根目录创建或修改 `.env`：

```dotenv
LLM_API_KEY=你的API密钥
LLM_BASE_URL=https://api.siliconflow.cn/v1
LLM_MODEL=Qwen/Qwen2.5-7B-Instruct
```

配置项说明：

| 变量 | 是否必需 | 说明 |
|---|---|---|
| `LLM_API_KEY` | 是 | 大模型服务的 API Key |
| `LLM_BASE_URL` | 否 | OpenAI 兼容 API 地址，默认使用 SiliconFlow |
| `LLM_MODEL` | 否 | 模型名称，默认使用 `Qwen/Qwen2.5-7B-Instruct` |

请勿公开 `.env` 或把真实 API Key 提交到版本控制系统。

## 运行多 Agent 流水线

### 使用自定义需求

```powershell
cd "E:\project-qing\multi_agent_system"
.\.venv\Scripts\python.exe .\main.py "写一个命令行待办事项程序"
```

程序会依次执行 PM、Coder 和 Reviewer，并把最终生成的 Python 代码写入当前工作目录中的：

```text
output_app.py
```

随后可以运行生成结果：

```powershell
.\.venv\Scripts\python.exe .\output_app.py
```

### 使用默认需求

不提供需求参数时：

```powershell
.\.venv\Scripts\python.exe .\main.py
```

系统默认要求大模型生成一个打印九九乘法表的 Python 脚本。

> **注意：** 运行 `main.py` 会覆盖当前目录中的 `output_app.py`。如果需要保留现有贪吃蛇游戏，请先复制或重命名该文件，例如：
>
> ```powershell
> Copy-Item .\output_app.py .\snake_game.py
> ```

## 项目结构

```text
multi_agent_system/
├── .env                 # 大模型服务配置，可能包含敏感信息
├── .venv/               # Python 虚拟环境
├── agents.py            # PM、Coder、Reviewer Agent 及 LLM 调用逻辑
├── graph.py             # 轻量级异步状态图引擎
├── main.py              # 多 Agent 流水线入口
├── models.py            # AgentState 全局共享状态模型
├── output_app.py        # 当前生成产物：Pygame 贪吃蛇游戏
├── requirements.txt     # 流水线自身的 Python 依赖
└── README.md             # 项目说明
```

## 工作原理

### 1. 产品经理 Agent

`product_manager_agent()` 接收用户原始需求，将其扩展为包含核心功能、交互逻辑和约束条件的 Markdown PRD。

### 2. 程序员 Agent

`developer_agent()` 根据 PRD 生成完整 Python 代码。如果审查员曾经驳回代码，它还会读取 `feedback` 并据此修改。

### 3. 审查员 Agent

`reviewer_agent()` 阅读 PRD 和生成代码，并返回以下状态之一：

- `APPROVED`：审核通过，工作流结束；
- `REJECTED`：审核不通过，反馈交还程序员继续修改。

### 4. 状态图

`StateGraph` 负责节点注册、条件跳转和最大执行步数控制。主流程如下：

```text
PM → Coder → Reviewer
              │
              └─ REJECTED → Coder → Reviewer → ...
```

Agent 之间通过 `AgentState` 共享以下数据：

- 用户任务 `task`
- 产品需求文档 `prd`
- Python 源代码 `code`
- 审核意见 `feedback`
- 当前流程状态 `status`
- 执行历史 `history`

## 当前限制

这是一个教学和原型项目，目前存在以下限制：

1. Reviewer 只通过大模型阅读代码，并不会真正运行代码、执行单元测试或进行静态检查。
2. API 调用尚未实现超时、重试、限流和完善的异常处理。
3. 生成程序所需的第三方依赖不会自动添加到 `requirements.txt`。
4. `output_app.py` 会被直接覆盖，没有自动备份。
5. 最大执行步数限制的是整个状态图的节点执行次数，并不严格等同于审核次数。
6. 大模型生成的代码不保证安全或正确，运行前应人工检查；不要在高权限环境中直接运行不可信代码。

## 常见问题

### 运行贪吃蛇时报 `ModuleNotFoundError: No module named 'pygame'`

安装 Pygame：

```powershell
.\.venv\Scripts\python.exe -m pip install pygame
```

### 运行流水线时报 API Key 或认证错误

检查 `.env` 中的 `LLM_API_KEY`、`LLM_BASE_URL` 和 `LLM_MODEL` 是否与所使用的大模型服务一致。

### 为什么 `output_app.py` 不是贪吃蛇了

`output_app.py` 是流水线的固定输出文件。每次运行 `main.py` 都会覆盖它。需要长期保留某个生成结果时，请先将它复制为其他文件名。

### 为什么最高分没有出现在脚本目录

贪吃蛇使用相对路径保存 `highscore.txt`，因此文件会生成在执行命令时的当前工作目录中。建议先进入项目目录，再运行游戏。
