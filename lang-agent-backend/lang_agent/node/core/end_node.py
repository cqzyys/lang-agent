from typing import Union

from pydantic import TypeAdapter

from .base import BaseNode, BaseNodeParam

__all__ = ["EndNode", "EndNodeParam"]


class EndNodeParam(BaseNodeParam):
    pass


class EndNode(BaseNode):
    type = "end"

    def __init__(self, param: Union[EndNodeParam, dict], **kwargs):
        adapter = TypeAdapter(EndNodeParam)
        param = adapter.validate_python(param)
        super().__init__(param, **kwargs)

    def invoke(self, state: dict):
        return state

    async def ainvoke(self, state: dict):
        return self.invoke(state)
