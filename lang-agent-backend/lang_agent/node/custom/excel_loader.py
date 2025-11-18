import asyncio
import traceback
import base64
import os
import shutil
from pathlib import Path
from typing import Optional, Union
import aiofiles
import pandas as pd
from pydantic import BaseModel, Field, TypeAdapter
from xid import XID

from langchain_core.messages import AIMessage
from langgraph.types import interrupt

from lang_agent.logger import get_logger
from lang_agent.util import objs_to_models
from ..core import BaseNode, BaseNodeData, BaseNodeParam

logger = get_logger(__name__)

__all__ = ["ExcelLoaderNode", "ExcelLoaderNodeParam"]

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.resolve()

class FileData(BaseModel):
    file_name: str = Field(..., description="文件名")
    file_content: str = Field(..., description="文件内容")

class ExcelLoaderNodeData(BaseNodeData):
    guiding_words: Optional[str] = Field(default="", description="引导词")

class ExcelLoaderNodeParam(BaseNodeParam):
    data: Optional[ExcelLoaderNodeData] = Field(default=None, description="节点数据")


class ExcelLoaderNode(BaseNode):
    type = "excel_loader"

    def __init__(self, param: Union[ExcelLoaderNodeParam, dict], **kwargs):
        adapter = TypeAdapter(ExcelLoaderNodeParam)
        param = adapter.validate_python(param)
        super().__init__(param, **kwargs)
        self.guiding_words = param.data.guiding_words

    async def ainvoke(self, state: dict):
        resume_state: dict = interrupt({
            "type": "file_upload",
            "message": self.guiding_words
        })
        try:
            files: list[FileData] = objs_to_models(
                resume_state.get("files", []),
                FileData
            )
            tmp_dir_path = PROJECT_ROOT / "tmp" / XID().string()
            os.makedirs(tmp_dir_path, exist_ok=True)
            contents: list[str] = []
            for file in files:
                _, encoded = file.file_content.split(";base64,", 1)
                file_data = base64.b64decode(encoded)
                file_path = tmp_dir_path / file.file_name
                async with aiofiles.open(file_path, "wb") as f:
                    await f.write(file_data)
                markdown = extract_excel(file_path)
                contents.append(markdown)
            await asyncio.get_event_loop().run_in_executor(
                None, shutil.rmtree, tmp_dir_path
            )
            return {"messages": [
                AIMessage(content="\n\n".join(contents), name=self.name)
            ]}
        except Exception as e:
            logger.info(traceback.format_exc())
            raise e

def extract_excel(excel_file_path, identifier="#")-> list[pd.DataFrame]:
    """
    基于特定标识符识别和分割表格，遍历Excel中的所有工作表
    
    Args:
        excel_file_path: Excel文件路径
        identifier: 用于标识表格开始的关键词
        
    Returns:
        dict: 以工作表名称为键，包含多个DataFrame列表为值的字典
    """
    # 读取所有工作表
    all_sheets = pd.read_excel(excel_file_path, sheet_name=None, header=None)
    result = ""
    for sheet_name, df_full in all_sheets.items():
        tables = []
        table_starts = []  
        # 查找所有标识符所在行
        for idx, row in df_full.iterrows():
            if row.astype(str).str.contains(identifier, case=False, na=False).any():
                table_starts.append(idx)
        # 如果没有找到标识符，则添加起始位置
        if not table_starts:
            table_starts.append(0)
        # 添加结束位置
        table_starts.append(len(df_full))
        # 根据标识符分割表格
        for i in range(len(table_starts)-1):
            start_idx = table_starts[i]
            end_idx = table_starts[i+1]
            # 查找实际数据范围（跳过标识符行和空行）
            actual_start = start_idx
            while actual_start < end_idx:
                if not df_full.iloc[actual_start].isna().all():
                    break
                actual_start += 1
            if actual_start < end_idx:
                # 找到下一个空行作为表的结尾
                actual_end = actual_start + 1
                while actual_end < end_idx:
                    if df_full.iloc[actual_end].isna().all():
                        break
                    actual_end += 1
                # 提取表格数据
                table_df = df_full.iloc[actual_start:actual_end].copy()
                # 设置第一行为表的标题
                if len(table_df) > 1:
                    table_df = table_df.fillna('')
                    table_df.columns = table_df.iloc[0]
                    table_df = table_df.drop(table_df.index[0]).reset_index(drop=True)
                    # 清理空列
                    table_df = table_df.dropna(axis=1, how='all')
                    # 将NaN值替换为空字符串
                    table_df = table_df.fillna('')
                    if not table_df.empty:
                        tables.append(table_df.to_markdown())
        result += "\n\n**"+ sheet_name+"**\n\n"+ "\n\n".join(tables)
    return result
