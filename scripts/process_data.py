"""Clean and chunk raw documents from the knowledge base data directory.

Reads all .txt and .md files, normalises whitespace, removes HTML artefacts,
and saves chunked JSON files ready for embedding.
"""

import json
import re
from pathlib import Path

from langchain.text_splitter import RecursiveCharacterTextSplitter

RAW_DIR = Path("backend/knowledge_base/data")
OUTPUT_DIR = Path("backend/knowledge_base/data/processed")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200


def clean_text(text: str) -> str:
    """Remove HTML tags, normalise whitespace, and strip control characters.

    Args:
        text: Raw text content.

    Returns:
        Cleaned text string.
    """
    # Remove HTML tags
    text = re.sub(r"<[^>]+>", " ", text)
    # Normalise whitespace (collapse multiple spaces/newlines)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def process_file(file_path: Path) -> list[dict]:
    """Load, clean, and chunk a single document.

    Args:
        file_path: Path to the raw document.

    Returns:
        List of chunk dictionaries with ``text``, ``source``, and ``chunk_id``.
    """
    raw = file_path.read_text(encoding="utf-8", errors="ignore")
    cleaned = clean_text(raw)

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
    )
    chunks = splitter.split_text(cleaned)

    return [
        {"text": chunk, "source": str(file_path), "chunk_id": i}
        for i, chunk in enumerate(chunks)
    ]


def main() -> None:
    """Process all raw documents and save chunked JSON output."""
    all_chunks: list[dict] = []

    for file_path in RAW_DIR.iterdir():
        if file_path.suffix.lower() not in (".txt", ".md"):
            continue
        if file_path.name == ".gitkeep":
            continue
        print(f"Processing: {file_path.name}")
        chunks = process_file(file_path)
        all_chunks.extend(chunks)
        print(f"  → {len(chunks)} chunks")

    output_file = OUTPUT_DIR / "chunks.json"
    with open(output_file, "w", encoding="utf-8") as fh:
        json.dump(all_chunks, fh, ensure_ascii=False, indent=2)

    print(f"\nTotal chunks: {len(all_chunks)}")
    print(f"Saved to: {output_file}")


if __name__ == "__main__":
    main()
