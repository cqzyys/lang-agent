import importlib
import pkgutil

from lang_agent.node.core import BaseNode

__all__ = ["NodeFactory"]

node_map = {}


class NodeFactory:
    @classmethod
    def instance(cls, param: dict, state_schema: dict) -> BaseNode:
        if node_map[param["type"]] is not None:
            return node_map[param["type"]](param, state_schema)
        raise ValueError(f'Unsupported Node Type: {param["type"]}')


def discover_nodes(package_name="lang_agent.node"):
    package = importlib.import_module(package_name)
    package_path = package.__path__
    for _, module_name, _ in pkgutil.walk_packages(package_path, package_name + "."):
        module = importlib.import_module(module_name)
        for attribute_name in dir(module):
            cls = getattr(module, attribute_name)
            if isinstance(cls, type) and issubclass(cls, BaseNode) and cls != BaseNode:
                if not cls.__subclasses__():
                    node_type = cls.type
                    node_map[node_type] = cls


discover_nodes()
