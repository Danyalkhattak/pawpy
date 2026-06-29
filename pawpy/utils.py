"""Shared utilities: banner, dedup writer, logging helpers."""

from __future__ import annotations

import logging
import os
from typing import Generator, Iterable, Set

from rich.console import Console
from rich.logging import RichHandler
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TaskProgressColumn,
    TextColumn,
    TimeRemainingColumn,
)

# ---------------------------------------------------------------------------
# Console & logging
# ---------------------------------------------------------------------------

console = Console()


def setup_logging(verbose: bool = False) -> logging.Logger:
    """Create and return the pawpy logger."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(console=console, rich_tracebacks=True)],
    )
    return logging.getLogger("pawpy")


# ---------------------------------------------------------------------------
# ASCII Banner
# ---------------------------------------------------------------------------

BANNER_TEXT = r"""
 ██████╗██╗   ██╗██████╗ ███████╗██████╗
██╔════╝╚██╗ ██╔╝██╔══██╗██╔════╝██╔══██╗
██║      ╚████╔╝ ██████╔╝█████╗  ██████╔╝
██║       ╚██╔╝  ██╔══██╗██╔══╝  ██╔══██╗
╚██████╗   ██║   ██████╔╝███████╗██║  ██║
 ╚═════╝   ╚═╝   ╚═════╝ ╚══════╝╚═╝  ╚═╝
"""

ETHICAL_WARNING = (
    "[bold red]⚠  ETHICAL USE ONLY[/bold red]\n"
    "This tool is intended for [bold]authorised security testing and educational purposes only[/bold].\n"
    "Unauthorised use against systems or accounts you do not own or have explicit\n"
    "permission to test is [bold red]illegal and unethical[/bold red].\n"
    "By proceeding, you confirm you have proper authorisation.\n"
)


def print_banner() -> None:
    """Display the Pawpy ASCII banner and ethical-use warning."""
    console.print(BANNER_TEXT, style="bold cyan")
    console.print(
        f"  v{__import__('pawpy').__version__}  |  The Most Powerful Educational Wordlist Generator",
        style="dim",
    )
    console.print()
    console.print(ETHICAL_WARNING)
    console.print()


# ---------------------------------------------------------------------------
# Dedup & streaming helpers
# ---------------------------------------------------------------------------


def dedup_stream(
    lines: Iterable[str],
    output_path: str,
) -> int:
    """Deduplicate an iterable of strings and write sorted output to *output_path*.

    Returns the number of unique lines written.
    """
    seen: Set[str] = set()
    count = 0
    tmp = output_path + ".tmp"
    with open(tmp, "w", encoding="utf-8", errors="ignore") as fh:
        for line in lines:
            line = line.rstrip("\n\r")
            if line and line not in seen:
                seen.add(line)
                fh.write(line + "\n")
                count += 1
    os.replace(tmp, output_path)
    return count


def iter_file(path: str) -> Generator[str, None, None]:
    """Yield non-empty lines from a text file."""
    with open(path, "r", encoding="utf-8", errors="ignore") as fh:
        for line in fh:
            stripped = line.rstrip("\n\r")
            if stripped:
                yield stripped


def make_progress() -> Progress:
    """Create a standard Rich progress bar."""
    return Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        TimeRemainingColumn(),
        console=console,
    )


# ---------------------------------------------------------------------------
# Confirmation prompt
# ---------------------------------------------------------------------------


def confirm_ethical_use() -> bool:
    """Prompt the user to confirm ethical use. Returns True on 'y'."""
    return (
        console.input(
            "[bold yellow]Do you confirm you have authorisation? [y/N]: [/bold yellow]"
        )
        .strip()
        .lower()
        == "y"
    )
