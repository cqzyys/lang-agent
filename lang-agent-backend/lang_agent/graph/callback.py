from typing import Any, Optional

from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.messages import BaseMessage

from lang_agent.logger import get_logger

logger = get_logger(__name__)

class LoggerOutputCallback(BaseCallbackHandler):

    @property
    def ignore_llm(self):
        return True

    @property
    def ignore_chain(self):
        return False

    def on_llm_start(
        self,
        serialized: dict[str, Any],
        prompts: list[str],
        *,
        run_id: str,
        parent_run_id: Optional[str] = None,
        tags: Optional[list[str]] = None,
        metadata: Optional[dict[str, Any]] = None,
        **kwargs: Any,
    ):
        logger.info("prompts: %s",prompts)

    def on_chain_end(self,
        outputs:dict[str, Any],
        *,
        run_id,
        parent_run_id = None,
        **kwargs
    ):
        messages = outputs.get("messages",[])
        for message in messages:
            if isinstance(message,BaseMessage):
                logger.info(
                    "Node:%s \n Content: %s",
                    message.name,message.content
                )
            else:
                logger.info("Content: %s",message)
