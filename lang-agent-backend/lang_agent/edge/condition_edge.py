from lang_agent.edge.util import Target
from lang_agent.util import complete_content


class ConditionEdge:
    def __init__(self, source: str, targets: list[Target]):
        self.source = source
        self.targets = targets

    def route(self, state: dict) -> str:
        for target in self.targets:
            if target.expr:
                expr = complete_content(target.expr, state)
                if eval(expr):
                    return target.target_name
                continue
            return target.target_name
