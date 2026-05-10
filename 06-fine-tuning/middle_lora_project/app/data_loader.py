"""
app/data_loader.py  –  Dataset loading and prompt formatting.
"""

import json
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

PROMPT_TEMPLATE = (
    "<|system|>\n"
    "You are a helpful AI assistant.\n"
    "<|user|>\n"
    "{instruction}\n"
    "<|assistant|>\n"
    "{response}"
)


def load_jsonl(path: str) -> List[Dict[str, str]]:
    """Read every line of a JSONL file and return a list of dicts."""
    records = []
    with open(path, encoding="utf-8") as fh:
        for lineno, line in enumerate(fh, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError as exc:
                logger.warning("Skipping malformed line %d: %s", lineno, exc)
    logger.info("Loaded %d records from %s", len(records), path)
    return records


def format_prompt(record: Dict[str, str]) -> str:
    """Convert a single instruction/response record into a chat prompt."""
    return PROMPT_TEMPLATE.format(
        instruction=record["instruction"],
        response=record["response"],
    )


def build_text_list(path: str) -> List[str]:
    """Return a list of formatted prompt strings ready for tokenisation."""
    records = load_jsonl(path)
    texts   = [format_prompt(r) for r in records]
    logger.info("Built %d formatted prompts.", len(texts))
    return texts
