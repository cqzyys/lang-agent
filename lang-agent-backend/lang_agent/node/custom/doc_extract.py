import traceback
import base64
import os
from typing import Optional, Union
from pathlib import Path
import asyncio
import shutil

from xid import XID
from pydantic import BaseModel, Field, TypeAdapter
import aiofiles

from langchain_core.language_models.base import BaseLanguageModel
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import BaseMessage, AIMessage
from langgraph.types import interrupt

from lang_agent.logger import get_logger
from lang_agent.setting.manager import resource_manager
from lang_agent.util import objs_to_models,aload_document
from ..core import BaseNode, BaseNodeData, BaseNodeParam

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.resolve()
DOWNLOAD_PATH = PROJECT_ROOT / "tmp/download"
DOWNLOAD_PATH.mkdir(parents=True, exist_ok=True)

logger = get_logger(__name__)

EXTRACT_PROMPT = """
## 角色
你是文献阅读与整理专家

## 任务
1、针对**输入文献**提炼以下内容：

主要研究内容

核心观点

研究方法（突出最新或关键方法）

研究结论

实证数据或理论框架

创新点

请按以下格式整理输出：
【文献序号】
【文献引用（GB/T格式）】
【主要研究内容】
【核心观点】
【研究方法】
【研究结论】
【实证数据或理论框架】
【创新点】

例如：

章子怡，杜冰，张荞之，等. 青少年心境障碍患者心理求助体验的质性研究[J]. 中华护理杂志，2025, 60(8): 947-953.
主要研究内容：
核心观点：
研究方法：
研究结论：
实证数据或理论框架：
创新点：

2、确保语言专业、信息完整、条理清晰。阅读整理完后再复查所有内容是否与输入文献一一对应，保证输出的内容真实、可靠。

## 输入文献
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

class DocExtractNodeData(BaseNodeData):
    guiding_words: Optional[str] = Field(default="", description="引导词")
    model: str = Field(..., description="模型名称")
    message_show: Optional[bool] = Field(default=True, description="是否显示消息")


class DocExtractNodeParam(BaseNodeParam):
    data: Optional[DocExtractNodeData] = Field(default=None, description="Node Data")


class DocExtractNode(BaseNode):
    type = "doc_extract"

    def __init__(self, param: Union[DocExtractNodeParam, dict], **kwargs):
        adapter = TypeAdapter(DocExtractNodeParam)
        param = adapter.validate_python(param)
        super().__init__(param, **kwargs)
        self.guiding_words = param.data.guiding_words
        self.model: BaseLanguageModel = resource_manager.models["llm"][param.data.model]
        self.message_show = param.data.message_show

    async def ainvoke(self, state: dict):
        try:
            resume_state: dict = interrupt({
                "type": "file_upload",
                "message": self.guiding_words
            })
            files: list[FileData] = objs_to_models(
                resume_state.get("files", []),FileData
            )
            tmp_dir_path = PROJECT_ROOT / "tmp" / XID().string()
            tmp_decompress_path = tmp_dir_path / "decompress"
            os.makedirs(tmp_dir_path, exist_ok=True)
            os.makedirs(tmp_decompress_path, exist_ok=True)
            messages: list[BaseMessage] = []
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
                    if self._decompress(tmp_file_path,tmp_decompress_path):
                        dir_path = tmp_decompress_path / file_name
                        extract_content = await self._extract_summary(dir_path)
                        logger.debug("####################")
                        logger.debug(
                            "%s extract_content: \n %s",
                            file_name,
                            extract_content
                        )
                        extension_file_name = file_name + ".md"
                        dowload_file_path = DOWNLOAD_PATH / extension_file_name
                        with open(dowload_file_path, "w", encoding="utf-8") as f:
                            f.write(extract_content)
                        message = AIMessage(
                            content = f"📥 [{file_name}](http://127.0.0.1:8810/api/v1/file/download/{extension_file_name})",
                            name = file_name,
                            message_show = self.message_show,
                        )
                        messages.append(message)
                    else:
                        logger.warning("Failed to extract %s",file.file_name)
            await asyncio.get_event_loop().run_in_executor(
                None, shutil.rmtree, tmp_dir_path
            )
            return {"messages": messages}
        except Exception as e:
            logger.info(traceback.format_exc())
            raise e

    async def _extract_summary(self, dir_path: Path) -> str:
        extract_list: list[str] = []
        for f in dir_path.iterdir():
            #logger.info("file: %s",f.name)
            docs = await aload_document(
                str(dir_path/f.name),
                strategy="fast",
                languages=["chi_sim", "eng"],
                chunking_strategy="by_title"
            )
            content = "\n".join([doc.page_content for doc in docs])
            #logger.info("content: %s",content)
            extract_message = await self._extract(content)
            extract_message = "#  "+f.name.split(".")[0]+"\n\n"+extract_message
            extract_list.append(extract_message)
        return "\n\n\n\n".join(extract_list)

    async def _extract(self, content: str) -> str:
        extract_template = ChatPromptTemplate.from_messages(
            [
                ("human", EXTRACT_PROMPT),
            ],
            template_format="mustache",
        )
        extract_chain = extract_template | self.model
        extract_message: BaseMessage = await extract_chain.ainvoke({"content": content})
        return extract_message.content


    def _decompress(self, file_path: Path, extract_path: Path) -> bool:
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
