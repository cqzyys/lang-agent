async def load_document(file_path: str):
    file_extension = file_path.rsplit(".",maxsplit=1)[-1].lower()
    match file_extension:
        case "pdf":
            from langchain_unstructured import UnstructuredLoader
            loader = UnstructuredLoader(
                file_path = file_path,
                partition_via_api=True,
                chunking_strategy="by_title",
                strategy="hi_res",
                languages=["chi_sim", "eng"],
            )
        case "txt":
            from langchain_community.document_loaders import TextLoader
            loader = TextLoader(file_path, encoding="utf-8")
        case "docx" | "md":
            from langchain_unstructured import UnstructuredLoader
            loader = UnstructuredLoader(file_path)
        case _:
            raise ValueError("Unsupported File Type")
    return await loader.aload()
