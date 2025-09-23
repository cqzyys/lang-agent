import json
from typing import Type
from pydantic import BaseModel

type_map = {
    "str": str,
    "int": int,
    "float": float,
    "bool": bool,
    "list": list,
}


def parse_type(content: str):
    return type_map[content]


def convert_str_to_type(value: str, target_type: str):
    if parse_type(target_type) is str:
        return value
    if parse_type(target_type) is int:
        return int(value)
    if parse_type(target_type) is float:
        return float(value)
    if parse_type(target_type) is bool:
        if value in ["true", "True"]:
            return True
        if value in ["false", "False"]:
            return False
        raise ValueError("错误的bool值")
    if parse_type(target_type) is list or target_type is dict:
        return json.loads(value)
    raise ValueError(f"不支持的类型: {target_type}")

def parse_json(content: any):
    try:
        if isinstance(content, str):
            if content.startswith("{") and content.endswith("}"):
                return json.loads(content)
            if content.startswith("[") and content.endswith("]"):
                return json.loads(content)
        return content
    except json.JSONDecodeError:
        return content

def error_to_str(error):
    match type(error).__name__:
        case "ValidationError":
            error_messages = [f"{err['loc']}: {err['msg']}" for err in error.errors()]
            return "\n".join(error_messages)
        case "HTTPException" | "IntegrityError" | "DatabaseError":
            return getattr(error, "detail", str(error))
        case "ExceptionGroup":
            exceptions = error.exceptions
            error_messages = []
            for e in exceptions:
                error_messages.append(error_to_str(e))
            return "\n".join(error_messages)
        case _ if hasattr(error, "detail"):
            return str(error.detail)
        case _:
            return f"{type(error).__name__}: {str(error)}"

def obj_to_model(source_instance,target_cls: Type[BaseModel]) -> BaseModel:
    return target_cls.model_validate(source_instance, from_attributes=True).model_dump()

def objs_to_models(source_instances,target_cls: Type[BaseModel]) -> list[BaseModel]:
    return [
        obj_to_model(
            source_instance,target_cls
        ) for source_instance in source_instances
    ]
