import re
from typing import Optional, Union
from lang_agent.util.util import complete_content
from pydantic import Field, TypeAdapter
from langchain_core.messages import AIMessage
from langchain_experimental.utilities import PythonREPL
from ..core import BaseNode, BaseNodeData, BaseNodeParam


class ExecutorNodeData(BaseNodeData):
    code: str = Field(..., description="Python代码")


class ExecutorNodeParam(BaseNodeParam):
    data: Optional[ExecutorNodeData] = Field(default=None, description="节点数据")


class ExecutorNode(BaseNode):
    type = "executor"

    def __init__(self, param: Union[ExecutorNodeParam, dict], **kwargs):
        adapter = TypeAdapter(ExecutorNodeParam)
        param = adapter.validate_python(param)
        super().__init__(param, **kwargs)
        self.code = param.data.code

    def invoke(self, state: dict):
        '''Sync Business Processing Logic'''
        self.code = complete_content(self.code, state)
        pattern = r'```python\s*(.*?)\s*```'
        match = re.search(pattern, self.code, re.DOTALL)
        if match:
            self.code = match.group(1)
        else:
            return {
                "messages": AIMessage(
                    content="Error: Invalid code block",
                    name=self.name
                )
            }
        result =  PythonREPL().run(self.code)
        return {"messages": AIMessage(content=result, name=self.name)}

    async def ainvoke(self, state: dict):
        '''ASync Business Processing Logic'''
        return self.invoke(state)
    