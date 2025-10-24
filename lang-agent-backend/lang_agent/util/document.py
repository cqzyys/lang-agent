from enum import Enum
import os

class Strategy(Enum):
    AUTO = "auto"
    FAST = "fast"
    HI_RES = "hi_res"
    OCR_ONLY = "ocr_only"
    VLM = "vlm"
async def load_document(file_path: str, strategy: Strategy = Strategy.FAST):
    file_extension = file_path.rsplit(".",maxsplit=1)[-1].lower()
    match file_extension:
        case "pdf":
            if os.environ.get("UNSTRUCTURED_API_KEY"):
                from langchain_unstructured import UnstructuredLoader
                loader = UnstructuredLoader(
                    file_path = file_path,
                    partition_via_api=True,
                    chunking_strategy="by_title",
                    strategy=strategy.value,
                    languages=["chi_sim", "eng"],
                )
            else:
                from langchain_community.document_loaders import PyPDFLoader
                loader = PyPDFLoader(file_path)
        case "txt" | "md":
            from langchain_community.document_loaders import TextLoader
            loader = TextLoader(file_path, encoding="utf-8")
        case "docx" | "doc":
            if os.environ.get("UNSTRUCTURED_API_KEY"):
                from langchain_community.document_loaders import (
                    UnstructuredWordDocumentLoader
                )
                loader = UnstructuredWordDocumentLoader(
                    file_path=file_path,
                    chunking_strategy="by_title",
                    strategy=strategy.value,
                    languages=["chi_sim", "eng"],
                )
            else:
                from langchain_community.document_loaders import (
                    Docx2txtLoader
                )
                loader = Docx2txtLoader(file_path)
        case _:
            raise ValueError("Unsupported File Type")
    return await loader.aload()
