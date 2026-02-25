"""Document ingestion pipeline for the ANSYS knowledge base."""

from pathlib import Path

from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Supported file extensions for ingestion
SUPPORTED_EXTENSIONS = {".txt", ".md", ".pdf"}


def load_documents(data_dir: str | Path = "backend/knowledge_base/data") -> list[Document]:
    """Load all supported documents from the data directory.

    Args:
        data_dir: Path to the directory containing raw documents.

    Returns:
        List of LangChain ``Document`` objects with text content and metadata.
    """
    data_path = Path(data_dir)
    documents: list[Document] = []

    for file_path in data_path.iterdir():
        if file_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            continue
        if file_path.name == ".gitkeep":
            continue

        text = _read_file(file_path)
        if text:
            documents.append(
                Document(
                    page_content=text,
                    metadata={"source": str(file_path), "filename": file_path.name},
                )
            )

    return documents


def chunk_documents(
    documents: list[Document],
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
) -> list[Document]:
    """Split documents into chunks suitable for embedding.

    Args:
        documents: List of documents to chunk.
        chunk_size: Maximum characters per chunk.
        chunk_overlap: Number of characters of overlap between consecutive chunks.

    Returns:
        List of chunked ``Document`` objects.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )
    return splitter.split_documents(documents)


def _read_file(file_path: Path) -> str:
    """Read text from a file, handling plain text and basic PDF extraction.

    Args:
        file_path: Path to the file to read.

    Returns:
        Extracted text content, or empty string on failure.
    """
    if file_path.suffix.lower() == ".pdf":
        try:
            import pypdf  # optional dependency

            reader = pypdf.PdfReader(str(file_path))
            return "\n".join(page.extract_text() or "" for page in reader.pages)
        except ImportError:
            print(f"pypdf not installed — skipping PDF: {file_path}")
            return ""
    else:
        try:
            return file_path.read_text(encoding="utf-8", errors="ignore")
        except OSError as exc:
            print(f"Could not read {file_path}: {exc}")
            return ""
