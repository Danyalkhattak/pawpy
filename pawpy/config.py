"""Global configuration object for Pawpy."""

from __future__ import annotations

import multiprocessing
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class PawpyConfig:
    """Central configuration holding every runtime setting."""

    # --- I/O ---
    output_file: str = "pawpy_wordlist.txt"
    profile_json: Optional[str] = None  # -j / --import-json
    multi_json: Optional[str] = None  # --multi
    rule_file: Optional[str] = None  # --rules
    templates: List[str] = field(default_factory=list)  # --template (repeatable)

    # --- Hybrid masks ---
    hybrid_left: Optional[str] = None  # --hybrid-left
    hybrid_right: Optional[str] = None  # --hybrid-right

    # --- Markov ---
    markov: bool = False
    markov_order: int = 2
    markov_count: int = 5000

    # --- Scoring / filtering ---
    min_strength: Optional[int] = None  # --min-strength (0-4)
    min_length: Optional[int] = None
    require_upper: bool = False
    require_lower: bool = False
    require_digit: bool = False
    require_special: bool = False

    # --- Modes ---
    lite: bool = False  # --lite
    extreme: bool = False  # --extreme
    gpu: bool = False  # --gpu

    # --- Performance ---
    threads: int = field(default_factory=lambda: multiprocessing.cpu_count() or 4)

    # --- Internal ---
    memory_threshold: int = 500_000_000  # bytes — switch to external sort above this
    chunk_size: int = 10_000_000  # lines per sorted chunk

    @property
    def is_lite(self) -> bool:
        return self.lite and not self.extreme

    @property
    def is_extreme(self) -> bool:
        return self.extreme

    def effective_threads(self) -> int:
        """Clamp threads to a sane range."""
        return max(1, min(self.threads, multiprocessing.cpu_count() * 4))
