from langchain_openai.chat_models import ChatOpenAI
import os
from functools import lru_cache

__api_key = os.environ.get("API_KEY", "")
__base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"


@lru_cache(maxsize= 10)
def get_llm(base_url = __base_url, api_key = __api_key):
    llm = ChatOpenAI(
        model="qwen-plus-0714", 
        temperature=0, 
        base_url = base_url,
        api_key= api_key
    )
    return llm