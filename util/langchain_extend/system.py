from langchain.schema.runnable import Runnable
from typing import List, TypeVar, Union, Any
from langchain_core.prompt_values import  ChatPromptValue
from pydantic import BaseModel
import json


_BM = TypeVar("_BM", bound=BaseModel)
_DictOrPydanticClass = Union[dict[str, Any], type[_BM], type]


class SystemMessageModifier(Runnable):
    def __init__(self, schema:_DictOrPydanticClass):
        self.schema = schema
        
    @property
    def dumps_schema_json(self):
        if issubclass(self.schema, BaseModel):
            return self.schema.model_json_schema()
        else:
            return json.dumps(dict(self.schema))
    def invoke(self, input:ChatPromptValue, config=None):
        system_message = input.messages[0]
        system_message.content = f"{system_message.content} \nYour response must be a JSON object that conforms to the following schema:\n {self.dumps_schema_json}"
        return input