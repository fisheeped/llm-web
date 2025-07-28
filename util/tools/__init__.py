from util.tools.math_cn import add, subtract, multiply, divide, power, sqrt, log, mod, exp 
from typing import List,Iterator
from langchain_core.tools.base import BaseTool


class Tools():
    def __init__(self, *tools: List[BaseTool]):
        self.tools = list(tools)
    
    @property
    def names(self):
        return [tool.name for tool in self.tools]
    
    def __iter__(self) -> Iterator[BaseTool]:
        return iter(self.tools)

    def __len__(self):
        return len(self.tools)

    def __getitem__(self, idx):
        return self.tools[idx]
    

    def to_string(self) -> str:
        """将工具集合转换为字符串格式"""
        return "\n".join(f"{i+1}. {tool.name}" for i, tool in enumerate(self.tools))
        
    def __str__(self):
        """用于 print(tools) 时的输出"""
        return f"Tools:\n{self.to_string()}"