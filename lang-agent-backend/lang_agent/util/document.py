import os

async def load_document(file_path: str, **unstructured_kwargs):
    file_extension = file_path.rsplit(".",maxsplit=1)[-1].lower()
    match file_extension:
        case "pdf":
            if os.environ.get("UNSTRUCTURED_API_KEY"):
                from langchain_community.document_loaders import (
                    UnstructuredPDFLoader
                )
                loader = UnstructuredPDFLoader(
                    file_path = file_path,
                    **unstructured_kwargs
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
                    **unstructured_kwargs
                )
            else:
                from langchain_community.document_loaders import (
                    Docx2txtLoader
                )
                loader = Docx2txtLoader(file_path)
        case _:
            raise ValueError("Unsupported File Type")
    return await loader.aload()
