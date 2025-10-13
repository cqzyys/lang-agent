import asyncio
import traceback
import base64
import os
import shutil
from typing import Optional, Union
from pathlib import Path


from xid import XID
from pydantic import BaseModel, Field, TypeAdapter
import aiofiles

from langchain_core.language_models.base import BaseLanguageModel
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import BaseMessage, AIMessage
from langgraph.types import interrupt

from lang_agent.logger import get_logger
from lang_agent.setting.manager import resource_manager
from lang_agent.util import objs_to_models,load_document
from ..core import BaseNode, BaseNodeData, BaseNodeParam

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.resolve()
DIR_PATH = PROJECT_ROOT / "tmp/download"

logger = get_logger(__name__)

REVIEW_PROMPT = """
## 角色
你是文献阅读信息萃取研究专家

## 任务
从**输入文献**中提取主要研究内容、研究方法、研究创新点以及结论，并与引用格式一一对应

## 注意事项
给出最后的内容再次核实是否与文献一一对应。

## 输入文献
{{content}}

## 输出格式
主要研究内容:
研究方法:
研究创新点:
结论:
"""

RESEARCH_PROMPT = """
## 任务
基于**主题**以及**文献概要**，以'研究现状->研究评述->本研究的研究价值及贡献'的逻辑，撰写一篇{{count}}字左右的文献综述

## 主题
{{theme}}

## 文献概要
{{review}}

## 具体要求
1、内容需按照现有核心概念、理论基础、研究方法、创新点、以及时间发展线等逻辑线进行阐述
2、阐述时不只是文献的堆叠和罗列，需要提出批判性思维，夹叙夹议的方式
3、用一句话指出已有研究的不足与空白，自然的引出本研究的必要性
"""

SUMMARY_PROMPT = """
## 角色
你是论文写作专家

## 任务
1、将各个主题的研究综述进行合并
2、核实上下文是否有重复叙述的内容以及长冗杂的描述，如果有请删除润色，同时各个主题要素之间的论述要给出逻辑关联及过渡衔接。

## 研究综述
{{content}}

"""

try:
    import patoolib
    PATOOL_AVAILABLE = True
except ImportError:
    PATOOL_AVAILABLE = False
    logger.warning(
        "patool module not installed. Please install it with `poetry add patool`."
    )

class FileData(BaseModel):
    file_name: str = Field(..., description="文件名")
    file_content: str = Field(..., description="文件内容")

class DocSummaryNodeData(BaseNodeData):
    guiding_words: Optional[str] = Field(default="", description="引导词")
    model: str = Field(..., description="模型名称")
    message_show: Optional[bool] = Field(default=True, description="是否显示消息")


class DocSummaryNodeParam(BaseNodeParam):
    data: Optional[DocSummaryNodeData] = Field(default=None, description="Node Data")


class DocSummaryNode(BaseNode):
    type = "doc_summary"

    def __init__(self, param: Union[DocSummaryNodeParam, dict], **kwargs):
        adapter = TypeAdapter(DocSummaryNodeParam)
        param = adapter.validate_python(param)
        super().__init__(param, **kwargs)
        self.guiding_words = param.data.guiding_words
        self.model: BaseLanguageModel = resource_manager.models["llm"][param.data.model]
        self.message_show = param.data.message_show

    async def ainvoke(self, state: dict):
        try:
            resume_state: dict = interrupt({
                "type": "doc_loader",
                "message": self.guiding_words
            })
            files: list[FileData] = objs_to_models(
                resume_state.get("files", []),FileData
            )
            tmp_dir_path = PROJECT_ROOT / "tmp" / XID().string()
            tmp_extract_path = tmp_dir_path / "extracted"
            os.makedirs(tmp_dir_path, exist_ok=True)
            os.makedirs(tmp_extract_path, exist_ok=True)
            research_dict: dict = {}
            for file in files:
                _, encoded = file.file_content.split(";base64,", 1)
                file_data = base64.b64decode(encoded)
                tmp_file_path = tmp_dir_path / file.file_name
                async with aiofiles.open(tmp_file_path, "wb") as f:
                    await f.write(file_data)
                file_name: str = file.file_name.split(".")[0]
                file_extension: str = file.file_name.split(".")[1].lower()
                compressed_extensions = {'zip', 'rar'}
                if file_extension in compressed_extensions:
                    if self._extract_archive(tmp_file_path,tmp_extract_path):
                        dir_path = tmp_extract_path / file_name
                        review_content = await self._review_summary(dir_path)
                        logger.debug("####################")
                        logger.debug(
                            "%s review_content: \n %s",
                            file_name,
                            review_content
                        )
                        research_content = await self._research(
                            file_name,review_content
                        )
                        logger.debug("####################")
                        logger.debug(
                            "%s research_content: \n %s",
                            file_name,
                            research_content
                        )
                        logger.debug("####################")
                        research_dict[file_name] = research_content
                    else:
                        logger.warning("Failed to extract %s",file.file_name)
            summary_content = await self._summary(str(research_dict))
            logger.debug(
                "summary_content: \n %s",
                summary_content
            )
            file_name = f"{self.name}.md"
            file_path = DIR_PATH / file_name
            DIR_PATH.mkdir(parents=True, exist_ok=True)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(summary_content)
            message = AIMessage(
                content = f"📥 [{self.name}](http://127.0.0.1:8810/api/v1/file/download/{file_name})",
                name = self.name,
                message_show = self.message_show,
            )
            return {"messages": message}
        except Exception as e:
            logger.info(traceback.format_exc())
            raise e

    async def _review_summary(self, dir_path: Path) -> str:
        review_list: list[str] = []
        for f in dir_path.iterdir():
            #logger.info("file: %s",f.name)
            docs = await load_document(str(dir_path/f.name))
            content = "\n".join([doc.page_content for doc in docs])
            #logger.info("content: %s",content)
            review_message = await self._review(content)
            review_list.append(review_message)
        return "\n".join(review_list)

    async def _review(self, content: str) -> str:
        review_template = ChatPromptTemplate.from_messages(
            [
                ("human", REVIEW_PROMPT),
            ],
            template_format="mustache",
        )
        review_chain = review_template | self.model
        review_message: BaseMessage = await review_chain.ainvoke({"content": content})
        return review_message.content

    async def _research(self, theme: str, review: str) -> str:
        research_template = ChatPromptTemplate.from_messages(
            [
                ("human", RESEARCH_PROMPT),
            ],
            template_format="mustache",
        )
        research_chain = research_template | self.model
        research_message: BaseMessage = await research_chain.ainvoke({
            "theme": theme,
            "review": review,
            "count": 3000
        })
        return research_message.content

    async def _summary(self, content: str) -> str:
        summary_template = ChatPromptTemplate.from_messages(
            [
                ("human", SUMMARY_PROMPT),
            ],
            template_format="mustache",
        )
        summary_chain = summary_template | self.model
        summary_message: BaseMessage = await summary_chain.ainvoke({"content": content})
        return summary_message.content

    def _extract_archive(self, file_path: Path, extract_path: Path) -> bool:
        if not PATOOL_AVAILABLE:
            logger.warning("patool not available, cannot extract archives")
            return False
        try:
            patoolib.extract_archive(
                str(file_path),
                outdir=str(extract_path),
                interactive=False
            )
            return True
        except Exception as e:
            logger.error("Failed to extract %s: %s",file_path,e)
            return False
