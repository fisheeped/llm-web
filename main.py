import streamlit as st
import json
import os
import time
import requests
from datetime import datetime
from util.share_button import load_share_button
from util.strings import getcode,get_repair_json
from util.cache_data import *
from util.md import latex
import copy
from streamlit_javascript import st_javascript

# 设置 Streamlit 页面
st.set_page_config(page_title="💬Novel Chat", layout="wide")
st.logo(image="assets/kl.png", size="large", icon_image="assets/kl.png")


st.title("💬Novel-Bot")
system_prompt_ = ""

branch_text_prompt = ""

# 侧边栏模型参数
current_url = st_javascript("window.location.href")
base_url = str(current_url).split("?")[0].split("/component/")[0].split("/~/")[0]

with st.sidebar:
    if "model_state" not in st.session_state:
        st.session_state.model_state = {}
    index = openai_model_list.index(st.session_state.model_state.get("model_version",openai_model_list[0]))
    model_version:str = st.selectbox("model",openai_model_list, index=index) # type: ignore
    model_name = api_model_card.get(model_version).get("model_name")
    system_prompt = api_model_card.get(model_version).get("system_prompt",system_prompt_)

    with st.expander("model api"):
        custom_model = st.text_input("api_model", st.session_state.model_state.get("custom_model", "") ,help="覆盖上面的Model")
        openai_key = st.text_input("api_key",st.session_state.model_state.get("openai_key", ""),help="覆盖自定义的api_key")
        openai_url = st.text_input("api_url",st.session_state.model_state.get("openai_url", ""),help="覆盖自定义的api_url")
    with st.expander("model args"):
        temperature = st.number_input("temperature",min_value=0.0,max_value=2.0,value=st.session_state.model_state.get("temperature", 0.1),step=0.01)
        thinking = st.checkbox('thinking', value= st.session_state.model_state.get("thinking", False))
        stream = st.checkbox('stream', value=st.session_state.model_state.get("stream", True))

    st.session_state.model_state["model_version"] = model_version
    st.session_state.model_state["openai_key"] = openai_key
    st.session_state.model_state["openai_url"] = openai_url
    st.session_state.model_state["custom_model"] = custom_model
    st.session_state.model_state["temperature"] = temperature
    st.session_state.model_state["thinking"] = thinking 
    st.session_state.model_state["stream"] = stream
    st.session_state.model_state["system_prompt"] = system_prompt_


    with st.expander("output args"):
        json_output = st.checkbox('json_output', value=st.session_state.model_state.get("json_output", False))
        st.session_state.model_state["json_output"] = json_output
    slide_col0,slide_col1 = st.columns(2)
    with slide_col0:
        if st.button('clear'):
            st.session_state.messages = []
    
    share_url = ""
    with slide_col1:
        if st.button("share",key="share"):
            cache_id = save_to_cache()
            share_url = f"{base_url}?c={cache_id}"
            st.session_state.model_state["share_url"] = share_url
    if len(st.session_state.model_state.get("share_url","")) > 0:
        st.code(st.session_state.model_state.get("share_url",""))
    
if len(openai_key) == 0:
    openai_key = api_model_card.get(model_version).get("openai_key")
if len(openai_url) == 0:
    openai_url = api_model_card.get(model_version).get("api_url")
if len(custom_model) > 0:
    model_name = custom_model
if len(system_prompt_) > 2:
    system_prompt = system_prompt_



post_url = f"{openai_url}/chat/completions"
# 初始化会话消息
if "messages" not in st.session_state:
    st.session_state.messages = []


# 存储响应内容
if 'content' not in st.session_state:
    st.session_state.content = ""

if 'reasoning_content' not in st.session_state:
    st.session_state.reasoning_content = ""

# 初始化折叠框的打开状态
if 'expander_opened' not in st.session_state:
    st.session_state.expander_opened = True



def messages_filter(messages):
    """只保留这三个角色"system","user","assistant" """
    # 从导数第二轮对话开始限制
    msg_nums = len(messages) - 2 
    msgs = []
    for i,msg in enumerate(messages):
        if msg["role"] == "assistant":
            # 去掉状态，省token
            if i < msg_nums:
                msg["content"] = msg["content"].rsplit("```background",1)[0]
        if msg.get("role") in ['system', 'user','assistant', 'tool', 'function']:
            msgs.append(msg)
    return msgs




for i, msg in enumerate(st.session_state.messages):
    if msg["role"] != "system":
        with st.chat_message(msg["role"]):
            if msg["role"] == "think":
                with st.expander(f"🧐", expanded=st.session_state.expander_opened):
                    st.write(msg["content"])
            else:
                st.write(latex(msg["content"]))
            elapsed_time = msg.get("elapsed_time","")
            with st.expander(f"editor\t\t\t\t{elapsed_time}"):
                new_content = st.text_area(label=f"msg-{i}",key = f"msg-{i}", value=msg["content"])
                col_0, col_1 = st.columns(2)
                with col_0:
                    edit_button = st.button("Edit", key=f"edit_{i}")
                    if edit_button:
                        st.session_state.messages[i]['content'] = new_content
                        st.rerun()
                with col_1:
                    delete_button = st.button("Delete", key=f"delete_{i}")
                    if delete_button:
                        del st.session_state.messages[i]
                        st.rerun()



# 处理流式输出
def stream_chat():
    start_time = time.time()  # 记录开始时间
    model_ = model_name.rsplit("-test", 1)[0]
    # messages_:list = copy.deepcopy(st.session_state.messages)
    messages_:list = messages_filter(st.session_state.messages)
    if isinstance(system_prompt, str) and len(system_prompt) > 0: 
        messages_.insert(0,{"role":"system", "content": system_prompt})
    
    data = {
        "model": model_,
        "messages": messages_,
        "temperature": temperature,
        "stream": stream,
        "enable_thinking": thinking
    }
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {openai_key}",
    }
    st.session_state.content = ""
    st.session_state.reasoning_content = ""
    reasoning_placeholder = st.empty()
    content_placeholder = st.empty()
    expander_opened_control = True  # 结论生成时只关闭一次
    # 生成格式化时间
    formatted_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")


    file_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S-%f")  # 微秒级精度，确保唯一
    log_dir = "logs"
    log_file = os.path.join(log_dir, f"{file_time}-chat.log")
    f =  open(log_file, 'a', encoding='utf-8') 
    f.write(f"=== REQUEST [{formatted_time}] ===\n")
    f.write(f"URL: {post_url}\n")
    f.write(f"Headers: {json.dumps(headers, ensure_ascii=False, indent=2)}\n")
    f.write(f"Body: {json.dumps(data, ensure_ascii=False, indent=2)}\n")
    f.write("\n" + "="*60 + "\n\n")

    # 发送请求
    response = requests.post(post_url, headers=headers, json=data, stream=stream)
    for line in response.iter_lines():
        f.write(line.decode("utf-8"))
        f.write("\n")
        decoded_line = line.decode("utf-8").strip()
        if len(line) < 1: continue
        if not decoded_line.startswith("data: {"): break
        try:
            data = json.loads(decoded_line[6:])
            delta = data["choices"][0]["delta"]
            if "content" in delta:
                if delta['content']:
                    st.session_state.content += delta["content"]
            # 兼容硅基流动格式，额外传输空数据串导致分支bug
            if "reasoning_content" in delta:
                st.session_state.reasoning_content += delta["reasoning_content"]
            elapsed_time = time.time() - start_time
            # 计算时间开销
            time_display = f"(Time taken: {elapsed_time:.2f} seconds)"
            if len(st.session_state.content) > 1:
                # 思考结束，关闭expander并更新结论内容
                if expander_opened_control:
                    expander_opened_control = False
                    with reasoning_placeholder.expander(f"🧐 COT", expanded=False):
                        st.write(st.session_state.reasoning_content)
                content_placeholder.success(f"✅ Result {formatted_time}\n{st.session_state.content}\n{time_display}")
            else:
                # 更新可折叠的思考内容
                with reasoning_placeholder.expander(f"🧐 COT {formatted_time}", expanded=True):
                    st.write(st.session_state.reasoning_content)
            
        except Exception as e:
            print(e, line)

    f.write("\n" + "="*60 + "\n")
    f.close()
    elapsed_time = time.time() - start_time
    total_time_display = f"(Time taken: {elapsed_time:.2f} seconds)"
    # 如果思考内容有更新，加入到消息中
    if len(st.session_state.reasoning_content.strip()) > 2:
        st.session_state.messages.append({"role": "think", "content": st.session_state.reasoning_content})
    
    # 更新会话状态
    st.session_state.messages.append({"role": "assistant", "content": st.session_state.content, "elapsed_time": total_time_display})


# 发送用户输入
if prompt := st.chat_input():
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    if stream:
        stream_chat()
    else:
        text = "非流式模式暂未实现"

    # 渲染 ECharts 图表
    st.rerun()



# 处理分享链接中的缓存文件参数
if 'c' in st.query_params:
    cache_id = st.query_params['c']
    load_from_cache(cache_id)
    st.query_params.pop('c')
    st.rerun()

