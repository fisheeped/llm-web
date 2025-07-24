from pydantic import BaseModel, Field
from typing import List, Tuple, Union, Dict, Literal
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import create_react_agent
from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate

from util.model import get_llm
from util.langchain_extend.system import SystemMessageModifier

# Define arithmetic tools
@tool
def add(a: float, b: float) -> float:
    """Adds two numbers."""
    return a + b


@tool
def subtract(a: float, b: float) -> float:
    """Subtracts the second number from the first."""
    return a - b


@tool
def multiply(a: float, b: float) -> float:
    """Multiplies two numbers."""
    return a * b


@tool
def divide(a: float, b: float) -> float:
    """Divides the first number by the second.

    Args:
        a (float): The dividend.
        b (float): The divisor.

    Returns:
        float: The result of the division.

    Raises:
        ValueError: If the divisor is zero.
    """
    if b == 0:
        raise ValueError('Cannot divide by zero.')
    return a / b


# Tools setup
TOOLS = [add, subtract, multiply, divide]

# Enhanced system prompt with clear decision-making guidelines
PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are an arithmetic assistant. Follow these guidelines:
    1. Perform operations in the given order.
    2. Ensure all operations are executed correctly.
    3. Report the final result."""),
    ("placeholder", "{messages}")
])

LLM = get_llm()
AGENT_EXECUTOR = create_react_agent(LLM, TOOLS, prompt=PROMPT)  # type: ignore

# Modified state structure to track check history and results
class PlanExecute(TypedDict):
    input: str
    plan: List[str]
    past_steps: List[Tuple]
    response: str
    messages: List[str]  # Add messages to track each step and result


class Plan(BaseModel):
    steps: List[str] = Field(description="Tasks to perform arithmetic operations")


class Response(BaseModel):
    response: str


class Act(BaseModel):
    action: Union[Response, Plan] = Field(description="Action to perform")


# Enhanced planning prompt with better context awareness
PLANNER_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """Create a focused arithmetic plan:
    1. Only include necessary operations
    2. Track what's already been done
    3. Ensure all operations are executed in sequence"""),
    ("placeholder", "{messages}"),
])


PLANNER = PLANNER_PROMPT | SystemMessageModifier(Plan) | LLM.with_structured_output(Plan)


# Improved replanning logic
REPLANNER_PROMPT = ChatPromptTemplate.from_template("""
Analyze the current situation and determine next steps:

Task: {input}
Completed steps: {past_steps}

Rules:
1. Don't repeat operations unless explicitly needed
2. Execute operations in sequence
3. End process after final operation

Available tools:
- add
- subtract
- multiply
- divide
""")


REPLANNER = REPLANNER_PROMPT | SystemMessageModifier(Act)  | LLM.with_structured_output(Act)


# # Enhanced execution step with state tracking
# async def execute_step(state: PlanExecute) -> Dict:
#     """Executes the next step in the plan.

#     Args:
#         state (PlanExecute): The current state of the execution.

#     Returns:
#         Dict: Updated state with past steps and messages.
#     """
#     plan = state["plan"]
#     if not plan:
#         return state

#     task = plan[0]
#     tool_map = {
#         "add": add,
#         "subtract": subtract,
#         "multiply": multiply,
#         "divide": divide
#     }

#     if task in tool_map:
#         result = tool_map[task]()
#         state["past_steps"].append((task, result))
#         state["messages"].append(f"Executed {task}: {result}")  # Log the message here
#         state["plan"] = state["plan"][1:]
#     else:
#         state["messages"].append(f"Unknown task: {task}")

#     return state

# Enhanced execution step with state tracking
async def execute_step(state: PlanExecute) -> Dict:
    """Executes the next step in the plan using AGENT_EXECUTOR.

    Args:
        state (PlanExecute): The current state of the execution.

    Returns:
        Dict: Updated state with past steps and messages.
    """
    plan = state["plan"]
    if not plan:
        return state

    task = plan[0]
    task_formatted = f"Execute the following task: {task}"
    
    agent_response = await AGENT_EXECUTOR.ainvoke(
        {"messages": [("user", task_formatted)]}
    )
    
    # Extract the result from the agent response
    result_message = agent_response["messages"][-1].content
    state["past_steps"].append((task, result_message))
    state["messages"].append(f"Executed {task}: {result_message}")  # Log the message here
    state["plan"] = state["plan"][1:]

    return state




# Initial planning step
async def plan_step(state: PlanExecute) -> Dict:
    """Generates a plan based on the user input.

    Args:
        state (PlanExecute): The current state of the execution.

    Returns:
        Dict: Updated state with the generated plan.
    """
    plan = await PLANNER.ainvoke({"messages": [("user", state["input"])]})
    state["plan"] = plan.steps
    state["messages"].append(f"Planned {plan}: {plan.steps}")  # Log the message here
    return state


# Enhanced replanning with better decision making
async def replan_step(state: PlanExecute) -> Dict:
    """Replans the steps based on the current state.

    Args:
        state (PlanExecute): The current state of the execution.

    Returns:
        Dict: Updated state with either the final response or a new plan.
    """
    output = await REPLANNER.ainvoke(state)

    if isinstance(output.action, Response):
        return {"response": output.action.response}

    state["plan"] = [step for step in output.action.steps
                    if step not in [s[0] for s in state["past_steps"]]]

    return state


# Enhanced end condition check
def should_end(state: PlanExecute) -> Literal['agent', 'end']:
    """Determines whether the workflow should end.

    Args:
        state (PlanExecute): The current state of the execution.

    Returns:
        Literal['agent', END]: The next node to execute or END if finished.
    """
    if not state["plan"]:
        return END
    return 'agent'


# Build the workflow
WORKFLOW = StateGraph(PlanExecute)
WORKFLOW.add_node("planner", plan_step)
WORKFLOW.add_node("agent", execute_step)
WORKFLOW.add_node("replan", replan_step)

WORKFLOW.add_edge(START, "planner")
WORKFLOW.add_edge("planner", "agent")
WORKFLOW.add_edge("agent", "replan")
WORKFLOW.add_conditional_edges("replan", should_end, ["agent", END])

APP = WORKFLOW.compile()


# Example usage
async def run_plan_and_execute():
    inputs = {
        "input": "Calculate (31233 * 31225) + 2",
        "past_steps": [],
        "messages": []  # Initialize an empty list for messages
    }
    config = {"recursion_limit": 15}

    async for event in APP.astream(inputs, config=config):
        print(event)
        print("\n\n")


if __name__ == "__main__":
    import asyncio
    asyncio.run(run_plan_and_execute())



