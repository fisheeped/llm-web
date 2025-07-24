from util.model import get_llm
from util.langchain_extend.system import SystemMessageModifier
from pydantic import BaseModel, Field

from langchain_core.prompts import ChatPromptTemplate


prompt_0 = ChatPromptTemplate.from_messages([
    ("system", """you are a helpful """),
    ("placeholder", "{messages}")
])


llm =  get_llm()


class GetWeather(BaseModel):
    """Get the current weather in a given location"""

    location: str = Field(..., description="The city and state, e.g. San Francisco, CA")


tools = [
    GetWeather,
    # {
    #     "type": "mcp",
    #     "server_label": "deepwiki",
    #     "server_url": "https://mcp.deepwiki.com/mcp",
    #     "require_approval": "never",
    # }
    ]

llm_with_tools = llm.bind_tools(tools)
ai_msg = llm_with_tools.invoke(
    "What transport protocols does the 2025-03-26 version of the MCP "
    "spec (modelcontextprotocol/modelcontextprotocol) support?"
)
ai_msg.content


