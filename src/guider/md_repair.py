import asyncio
import logging
from pathlib import Path
from typing import Literal, List

from langchain_core.tools import tool
from pydantic import BaseModel, Field

from ..assets import AssetsInfo
from ..core.llm_core import run_llm_loop

logger = logging.getLogger("TestGen.md_repair")

PROMPT = """
You are cleaning chunk {chunk_index}/{total_chunks} of the Markdown file "{file_name}".
Clean the following chunk (≈300 characters, split along line boundaries), fixing formatting issues while preserving the original wording:

```
{content}
```

Requirements:
1. Remove redundant blank lines or trailing spaces while preserving intentional spacing/indentation.
2. Fix obvious Markdown syntax issues (headings, bullet lists, fenced code blocks, links).
3. Do NOT paraphrase or omit text; only adjust formatting.
4. After cleaning, call the tool `submit_clean_chunk` with the final chunk text. Do not attempt to save the whole file yourself.

Follow the JSON output instructions below:
{format_information}
"""

CLEAN_OUTPUT_DIR = Path(AssetsInfo.good_guide_path)
CURRENT_FILE_NAME: str = ""
EXPECTED_COMPACT_LEN: int = 0
CLEANED_CHUNKS: List[str] = []


class MdRepairOutput(BaseModel):
    status: Literal["completed", "failed"]
    message: str = Field(..., max_length=500)


def _set_current_file(file_name: str, content: str):
    global CURRENT_FILE_NAME, EXPECTED_COMPACT_LEN
    CURRENT_FILE_NAME = file_name
    EXPECTED_COMPACT_LEN = _compact_length(content)


def _compact_length(text: str) -> int:
    return len("".join(ch for ch in text if not ch.isspace()))


def _split_into_chunks(text: str, target: int = 20000) -> List[str]:
    lines = text.splitlines(keepends=True)
    chunks: List[str] = []
    current: List[str] = []
    current_len = 0
    for line in lines:
        if current and current_len + len(line) > target:
            chunks.append("".join(current))
            current = []
            current_len = 0
        current.append(line)
        current_len += len(line)
    if current:
        chunks.append("".join(current))
    if not chunks:
        return [text]
    return chunks


def _reset_chunk_buffer():
    global CLEANED_CHUNKS
    CLEANED_CHUNKS = []


@tool
def submit_clean_chunk(cleaned_chunk: str) -> str:
    """
    Store the cleaned chunk provided by the LLM for later assembly.
    """
    if not cleaned_chunk.strip():
        return "FAILED: cleaned chunk is empty"
    CLEANED_CHUNKS.append(cleaned_chunk)
    return "SUCCESS: chunk accepted"


def _write_clean_markdown(file_name: str, cleaned_content: str) -> None:
    cleaned_len = _compact_length(cleaned_content)
    reference = EXPECTED_COMPACT_LEN or 1
    drift = abs(cleaned_len - reference) / reference
    if drift > 0.2:
        raise ValueError(
            f"Cleaned content deviates too much from original length ({drift:.2%})."
        )
    CLEAN_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    target_path = CLEAN_OUTPUT_DIR / file_name
    target_path.write_text(cleaned_content, encoding="utf-8")
    logger.info("Wrote cleaned file to %s", target_path)


async def _repair_chunk(chunk: str, chunk_index: int, total_chunks: int, file_name: str) -> None:
    pre_count = len(CLEANED_CHUNKS)
    await run_llm_loop(
        prompt_template=PROMPT,
        output_pydantic=MdRepairOutput,
        format_args={
            "file_name": file_name,
            "chunk_index": chunk_index,
            "total_chunks": total_chunks,
            "content": chunk,
        },
        tool_list=[submit_clean_chunk],
        max_tool_iterations=6,
    )
    if len(CLEANED_CHUNKS) == pre_count:
        raise RuntimeError("Chunk processed without submitting cleaned text.")


async def _repair_single_file(file_path: Path) -> str:
    content = file_path.read_text(encoding="utf-8")
    _set_current_file(file_path.name, content)
    chunks = _split_into_chunks(content, target=7500)
    _reset_chunk_buffer()

    total = len(chunks)
    logger.info("File %s split into %d chunks", file_path.name, total)

    for idx, chunk in enumerate(chunks, start=1):
        logger.debug("Cleaning chunk %d/%d (len=%d)", idx, total, len(chunk))
        await _repair_chunk(chunk, idx, total, file_path.name)

    cleaned_text = "".join(CLEANED_CHUNKS)
    _write_clean_markdown(file_path.name, cleaned_text)
    return "completed"


def repair_markdown_file(file_path: str) -> str:
    """
    Repair a single markdown file and save the cleaned version into the configured directory.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File does not exist: {file_path}")

    logger.info("Repairing markdown: %s", path.name)
    message = asyncio.run(_repair_single_file(path))
    logger.info("Repair completed for %s: %s", path.name, message)
    return message
