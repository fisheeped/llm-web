import uuid
import streamlit.components.v1 as components
import json5 as json
import time
import streamlit as st
import os


with open("assets/data.json","r",encoding= 'utf-8') as f:
    data = f.read()

base_dir = "/mnt/nodestor/cluster_share_folder/user-fs/train/yuyang"
model_name = "yy"

api_key = os.environ.get("API_KEY", "")
api_model_card = {
    "qwen-plus-lingfeng":{
        "model_name": "qwen-plus-latest", 
        "openai_key": api_key, 
        "api_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "system_prompt": f"你是一个名叫“小云”的人工智能助手，性格温和、知识渊博，擅长解答用户的各种问题，由世凌风研发和训练。这里还有些其他数据:{data}"
        
    },
    "qwen":{
        "model_name": "qwen-plus-latest",
        "openai_key": api_key, 
        "api_url": "https://dashscope.aliyuncs.com/compatible-mode/v1"
    }
}


openai_model_list = [i for i in api_model_card]
system_prompt = "You are a helpful assistant."
qwen3_no_thinking_template = "{%- if tools %}\n    {{- '<|im_start|>system\\n' }}\n    {%- if messages[0].role == 'system' %}\n        {{- messages[0].content + '\\n\\n' }}\n    {%- endif %}\n    {{- \"# Tools\\n\\nYou may call one or more functions to assist with the user query.\\n\\nYou are provided with function signatures within <tools></tools> XML tags:\\n<tools>\" }}\n    {%- for tool in tools %}\n        {{- \"\\n\" }}\n        {{- tool | tojson }}\n    {%- endfor %}\n    {{- \"\\n</tools>\\n\\nFor each function call, return a json object with function name and arguments within <tool_call></tool_call> XML tags:\\n<tool_call>\\n{\\\"name\\\": <function-name>, \\\"arguments\\\": <args-json-object>}\\n</tool_call><|im_end|>\\n\" }}\n{%- else %}\n    {%- if messages[0].role == 'system' %}\n        {{- '<|im_start|>system\\n' + messages[0].content + '<|im_end|>\\n' }}\n    {%- endif %}\n{%- endif %}\n{%- set ns = namespace(multi_step_tool=true, last_query_index=messages|length - 1) %}\n{%- for message in messages[::-1] %}\n    {%- set index = (messages|length - 1) - loop.index0 %}\n    {%- if ns.multi_step_tool and message.role == \"user\" and not(message.content.startswith('<tool_response>') and message.content.endswith('</tool_response>')) %}\n        {%- set ns.multi_step_tool = false %}\n        {%- set ns.last_query_index = index %}\n    {%- endif %}\n{%- endfor %}\n{%- for message in messages %}\n    {%- if (message.role == \"user\") or (message.role == \"system\" and not loop.first) %}\n        {{- '<|im_start|>' + message.role + '\\n' + message.content + '<|im_end|>' + '\\n' }}\n    {%- elif message.role == \"assistant\" %}\n        {%- set content = message.content %}\n        {%- set reasoning_content = '' %}\n        {%- if message.reasoning_content is defined and message.reasoning_content is not none %}\n            {%- set reasoning_content = message.reasoning_content %}\n        {%- else %}\n            {%- if '</think>' in message.content %}\n                {%- set content = message.content.split('</think>')[-1].lstrip('\\n') %}\n                {%- set reasoning_content = message.content.split('</think>')[0].rstrip('\\n').split('<think>')[-1].lstrip('\\n') %}\n            {%- endif %}\n        {%- endif %}\n        {%- if loop.index0 > ns.last_query_index %}\n            {%- if loop.last or (not loop.last and reasoning_content) %}\n                {{- '<|im_start|>' + message.role + '\\n<think>\\n' + reasoning_content.strip('\\n') + '\\n</think>\\n\\n' + content.lstrip('\\n') }}\n            {%- else %}\n                {{- '<|im_start|>' + message.role + '\\n' + content }}\n            {%- endif %}\n        {%- else %}\n            {{- '<|im_start|>' + message.role + '\\n' + content }}\n        {%- endif %}\n        {%- if message.tool_calls %}\n            {%- for tool_call in message.tool_calls %}\n                {%- if (loop.first and content) or (not loop.first) %}\n                    {{- '\\n' }}\n                {%- endif %}\n                {%- if tool_call.function %}\n                    {%- set tool_call = tool_call.function %}\n                {%- endif %}\n                {{- '<tool_call>\\n{\"name\": \"' }}\n                {{- tool_call.name }}\n                {{- '\", \"arguments\": ' }}\n                {%- if tool_call.arguments is string %}\n                    {{- tool_call.arguments }}\n                {%- else %}\n                    {{- tool_call.arguments | tojson }}\n                {%- endif %}\n                {{- '}\\n</tool_call>' }}\n            {%- endfor %}\n        {%- endif %}\n        {{- '<|im_end|>\\n' }}\n    {%- elif message.role == \"tool\" %}\n        {%- if loop.first or (messages[loop.index0 - 1].role != \"tool\") %}\n            {{- '<|im_start|>user' }}\n        {%- endif %}\n        {{- '\\n<tool_response>\\n' }}\n        {{- message.content }}\n        {{- '\\n</tool_response>' }}\n        {%- if loop.last or (messages[loop.index0 + 1].role != \"tool\") %}\n            {{- '<|im_end|>\\n' }}\n        {%- endif %}\n    {%- endif %}\n{%- endfor %}\n{%- if add_generation_prompt %}\n    {{- '<|im_start|>assistant\\n<think>\\n\\n</think>\\n\\n' }}\n    {%- endif %}"





# 保存session state到缓存文件
def save_to_cache():
    cache_id = f"{str(time.time())}{str(uuid.uuid4())}"
    cache_file = f".cache/cache_{cache_id}.json"
    with open(cache_file, 'w') as f:
        cache_data = {
            "messages": st.session_state.messages,
            "model_state": st.session_state.model_state
        }
        json.dump(cache_data, f)
    return cache_id

# 加载缓存文件到session state
def load_from_cache(cache_id):
    cache_file_ = f".cache/cache_{cache_id}.json"
    if os.path.exists(cache_file_):
        with open(cache_file_, 'r') as f:
            cache_data = json.load(f)
            st.session_state.messages = cache_data['messages']
            st.session_state.model_state = cache_data['model_state']
    else:
        st.error("链接不存在或者，已经被取消了")