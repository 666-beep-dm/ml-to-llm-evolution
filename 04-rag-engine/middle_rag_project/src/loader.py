"""
Document loader — supports .txt and .json files from a directory.
Returns a list of LangChain Document objects.
"""

import json
import logging
from pathlib import Path

from langchain_core.documents import Document

logger = logging.getLogger(__name__)


def load_txt(path: Path) -> list[Document]:
    """Load a plain-text file as a single Document."""
    text = path.read_text(encoding="utf-8").strip()
    if not text:
        logger.warning("Empty file skipped: %s", path)
        return []
    return [Document(page_content=text, metadata={"source": str(path)})]


def load_json(path: Path) -> list[Document]:
    """
    Load a JSON file.

    Supported shapes:
    - A single object with a "text" or "content" key → one Document.
    - A list of objects, each with a "text" or "content" key → many Documents.
    - A plain string value at the root → one Document.
    """
    raw = json.loads(path.read_text(encoding="utf-8"))
    docs: list[Document] = []

    items: list = raw if isinstance(raw, list) else [raw]

    for i, item in enumerate(items):
        if isinstance(item, str):
            content = item
        elif isinstance(item, dict):
            content = item.get("text") or item.get("content") or ""
        else:
            logger.warning("Unsupported JSON item type at index %d in %s", i, path)
            continue

        content = content.strip()
        if content:
            docs.append(
                Document(
                    page_content=content,
                    metadata={"source": str(path), "index": i},
                )
            )

    return docs


def load_documents(data_dir: str) -> list[Document]:
    """
    Recursively load all .txt and .json files from *data_dir*.

    Raises:
        FileNotFoundError: if the directory does not exist.
    """
    directory = Path(data_dir)
    if not directory.exists():
        raise FileNotFoundError(f"Data directory not found: {directory}")

    loaders: dict[str, callable] = {
        ".txt": load_txt,
        ".json": load_json,
    }

    documents: list[Document] = []
    for suffix, loader in loaders.items():
        for file_path in sorted(directory.rglob(f"*{suffix}")):
            logger.info("Loading %s", file_path)
            try:
                documents.extend(loader(file_path))
            except Exception as exc:
                logger.error("Failed to load %s: %s", file_path, exc)

    logger.info("Total documents loaded: %d", len(documents))
    return documents
