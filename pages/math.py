import streamlit as st
import asyncio
from typing import Dict, AsyncGenerator

# 假设你已有 LangGraph 的 APP 实例
from util.graph.math_cn import APP  # 替换为实际路径
from util import run_async_function


st.set_page_config(page_title="四则运算助手", layout="centered")
st.title("数学助手")

# 聊天记录容器
if "messages" not in st.session_state:
    st.session_state.messages = []

# 用户输入区域
if prompt := st.chat_input("请输入计算指令，例如：Calculate (31233 * 31225) + 2"):
    # 记录用户消息
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 用 st.chat_message 渲染用户输入
    with st.chat_message("user"):
        st.markdown(prompt)

    # 执行 LangGraph 流程并记录 assistant 回复
    with st.chat_message("assistant"):
        with st.spinner("正在分析并计算..."):

            async def run_workflow(input_text: str) -> AsyncGenerator[Dict, None]:
                inputs = {
                    "input": input_text,
                    "past_steps": [],
                    "messages": []
                }
                config = {"recursion_limit": 15}
                async for event in APP.astream(inputs, config=config):
                    yield event

            async def run_and_render():
                final_response = None
                async for event in run_workflow(prompt):
                    step_name, state = next(iter(event.items()))

                    if step_name == "planner":
                        st.markdown("📋 **规划步骤：**")
                        for i, step in enumerate(state["plan"], 1):
                            st.markdown(f"{i}. {step}")

                    elif step_name == "agent":
                        st.markdown("⚙️ **执行过程：**")
                        for step, result in state.get("past_steps", []):
                            emoji = "✅" if "结果" in result or "是" in result else "⚠️"
                            st.markdown(f"{emoji} **{step}**: {result}")

                    elif step_name == "replan":
                        final_response = state.get("response")
                        if final_response:
                            st.markdown("🔁 **重规划响应：**")
                            st.markdown(f"`{final_response}`")

                if final_response:
                    st.success(f"✅ 最终答案：{final_response}")
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": f"最终答案是：{final_response}"
                    })

            run_async_function(run_and_render())

