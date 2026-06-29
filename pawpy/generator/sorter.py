"""Billion-scale external merge sort for wordlists.

When the candidate set exceeds available memory, this module streams
candidates to temporary sorted chunks and then merge-sorts them into
the final output.
"""

from __future__ import annotations

import heapq
import logging
import os
import tempfile
from typing import Generator, List

logger = logging.getLogger("pawpy.generator.sorter")


def _sort_and_write_chunk(lines: List[str], chunk_path: str) -> None:
    """Sort a list of lines and write to a temp file."""
    lines.sort()
    with open(chunk_path, "w", encoding="utf-8", errors="ignore") as fh:
        for line in lines:
            fh.write(line + "\n")


def external_merge_sort(
    lines: Generator[str, None, None],
    output_path: str,
    memory_threshold: int = 500_000_000,
    chunk_line_count: int = 5_000_000,
) -> int:
    """Sort and deduplicate a stream of lines using external merge sort.

    When the in-memory buffer exceeds *memory_threshold* bytes, the buffer
    is sorted, deduplicated, and flushed to a temporary file.  After all
    input is consumed, the sorted chunks are merged.

    Args:
        lines: Generator yielding candidate password strings.
        output_path: Final output file path.
        memory_threshold: Approximate memory limit in bytes.
        chunk_line_count: Maximum lines per sorted chunk.

    Returns:
        Number of unique lines written.
    """
    buffer: List[str] = []
    chunk_files: List[str] = []
    seen_in_buffer: set = set()
    total_written = 0
    est_size = 0

    def flush_buffer():
        nonlocal buffer, seen_in_buffer, est_size
        if not buffer:
            return
        _, chunk_path = tempfile.mkstemp(suffix=".chunk", prefix="pawpy_")
        _sort_and_write_chunk(buffer, chunk_path)
        chunk_files.append(chunk_path)
        logger.info(
            "Flushed chunk %d: %d lines -> %s",
            len(chunk_files),
            len(buffer),
            chunk_path,
        )
        buffer = []
        seen_in_buffer = set()
        est_size = 0

    for line in lines:
        line = line.strip()
        if not line:
            continue

        if line not in seen_in_buffer:
            buffer.append(line)
            seen_in_buffer.add(line)
            est_size += len(line.encode("utf-8")) + 1

            if est_size >= memory_threshold or len(buffer) >= chunk_line_count:
                flush_buffer()

    # Flush remaining buffer
    flush_buffer()

    if not chunk_files:
        # Everything fit in memory – just write sorted output
        buffer.sort()
        with open(output_path, "w", encoding="utf-8") as fh:
            prev = None
            for line in buffer:
                if line != prev:
                    fh.write(line + "\n")
                    total_written += 1
                    prev = line
        return total_written

    # K-way merge using heapq
    file_handles = []
    try:
        for path in chunk_files:
            fh = open(path, "r", encoding="utf-8", errors="ignore")
            first_line = fh.readline().strip()
            if first_line:
                file_handles.append((first_line, fh))

        heapq.heapify(file_handles)

        with open(output_path, "w", encoding="utf-8") as out_fh:
            prev = None
            while file_handles:
                line, fh = heapq.heappop(file_handles)
                if line != prev:
                    out_fh.write(line + "\n")
                    total_written += 1
                    prev = line
                next_line = fh.readline().strip()
                if next_line:
                    heapq.heappush(file_handles, (next_line, fh))
                else:
                    fh.close()
    finally:
        # Clean up temp files
        for _, fh in file_handles:
            try:
                fh.close()
            except Exception:
                pass
        for path in chunk_files:
            try:
                os.unlink(path)
            except Exception:
                pass

    return total_written
