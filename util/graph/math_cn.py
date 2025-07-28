from pydantic import BaseModel, Field
from typing import List, Tuple, Union, Dict, Literal
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import create_react_agent
from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate

from util.model import get_llm
from util.langchain_extend.system import SystemMessageModifier
from util.tools import add, subtract, multiply, divide, power, sqrt, log, mod, exp , Tools


# 工具列表
TOOLS = Tools(add, subtract, multiply, divide, power, sqrt, log, mod, exp  )

# 系统提示词，说明任务规则
PROMPT = ChatPromptTemplate.from_messages([
    ("system", """你是一个四则运算助手，请遵循以下规则：
    1. 按照给定顺序执行操作；
    2. 确保每步运算正确；
    3. 返回最终结果。"""),
    ("placeholder", "{messages}")
])

# 初始化语言模型和 agent
LLM = get_llm()
AGENT_EXECUTOR = create_react_agent(LLM, TOOLS, prompt=PROMPT)  # type: ignore

# 状态结构：包含输入、计划、执行历史、最终响应和中间消息
class PlanExecute(TypedDict):
    input: str
    plan: List[str]
    past_steps: List[Tuple]
    response: str
    messages: List[str]  # 用于记录每步执行的中间信息

# 定义数据模型
class Plan(BaseModel):
    steps: List[str] = Field(description="需要执行的运算步骤")

# 响应则直接结束
class Response(BaseModel):
    response: str

class Act(BaseModel):
    action: Union[Response, Plan] = Field(description="下一步动作")

# 计划提示词：用于引导 LLM 生成运算计划
PLANNER_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """创建一个聚焦的数学运算计划：
    1. 仅包含必要的操作；
    2. 跟踪已完成的步骤；
    3. 确保顺序执行。"""),
    ("placeholder", "{messages}"),
])

# 计划器组件
PLANNER = PLANNER_PROMPT | SystemMessageModifier(Plan) | LLM.with_structured_output(Plan)

# 重规划提示词：当需要调整或补全计划时使用
REPLANNER_PROMPT = ChatPromptTemplate.from_template("""
分析当前状态并决定下一步：

任务: {input}
已完成步骤: {past_steps}

规则：
1. 除非明确需要，否则不重复执行；
2. 按顺序完成任务；
3. 所有操作完成后结束流程。

可用工具：
""" + TOOLS.to_string())

# 重规划器组件
REPLANNER = REPLANNER_PROMPT | SystemMessageModifier(Act)  | LLM.with_structured_output(Act)

# 执行计划中的一步
async def execute_step(state: PlanExecute) -> Dict:
    """执行计划中的下一步任务

    参数：
        state (PlanExecute): 当前状态

    返回：
        Dict: 更新后的状态，包括历史记录和日志信息
    """
    plan = state["plan"]
    if not plan:
        return state

    task = plan[0]
    task_formatted = f"Execute the following task: {task}"
    
    agent_response = await AGENT_EXECUTOR.ainvoke(
        {"messages": [("user", task_formatted)]}
    )
    
    result_message = agent_response["messages"][-1].content
    state["past_steps"].append((task, result_message))
    state["messages"].append(f"执行 {task}: {result_message}")  # 添加日志
    state["plan"] = state["plan"][1:]

    return state

# 第一步：根据用户输入生成运算计划
async def plan_step(state: PlanExecute) -> Dict:
    """根据输入生成初始运算计划

    参数：
        state (PlanExecute): 当前状态

    返回：
        Dict: 包含新计划的状态
    """
    plan = await PLANNER.ainvoke({"messages": [("user", state["input"])]})
    state["plan"] = plan.steps
    state["messages"].append(f"计划生成 {plan}: {plan.steps}")
    return state

# 动态修复或补全计划
async def replan_step(state: PlanExecute) -> Dict:
    """根据当前状态重新规划或生成最终响应

    参数：
        state (PlanExecute): 当前状态

    返回：
        Dict: 如果是最终响应则直接返回，否则更新计划
    """
    output = await REPLANNER.ainvoke(state)

    if isinstance(output.action, Response):
        return {"response": output.action.response}

    # 跳过已完成的任务
    state["plan"] = [step for step in output.action.steps
                    if step not in [s[0] for s in state["past_steps"]]]

    return state

# 判断是否执行结束
def should_end(state: PlanExecute) -> Literal['agent', 'end']:
    """判断是否完成所有任务

    参数：
        state (PlanExecute): 当前状态

    返回：
        'agent' 或 'end' 表示下一步的节点
    """
    if not state["plan"]:
        return END
    return 'agent'

# 构建 LangGraph 流程图
WORKFLOW = StateGraph(PlanExecute)
WORKFLOW.add_node("planner", plan_step)
WORKFLOW.add_node("agent", execute_step)
WORKFLOW.add_node("replan", replan_step)

WORKFLOW.add_edge(START, "planner")
WORKFLOW.add_edge("planner", "agent")
WORKFLOW.add_edge("agent", "replan")
WORKFLOW.add_conditional_edges("replan", should_end, ["agent", END])

APP = WORKFLOW.compile()

# 示例调用方法
async def run_plan_and_execute():
    inputs = {
        "input": "Calculate (31233 * 31225) + 2",
        "past_steps": [],
        "messages": []  # 初始化日志列表
    }
    config = {"recursion_limit": 15}

    async for event in APP.astream(inputs, config=config):
        print(event)
        print("\n\n")

if __name__ == "__main__":
    import asyncio
    asyncio.run(run_plan_and_execute())
