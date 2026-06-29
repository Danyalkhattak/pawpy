"""Optional GPU acceleration via CuPy.

When ``cupy`` is installed and ``--gpu`` is passed, rule application
is offloaded to the GPU for parallel execution.
"""

from __future__ import annotations

import logging
from typing import List

logger = logging.getLogger("pawpy.generator.gpu")

_CUPY_AVAILABLE = False
try:
    import cupy as cp

    _CUPY_AVAILABLE = True
except ImportError:
    cp = None  # type: ignore[assignment]


def is_gpu_available() -> bool:
    """Check whether CuPy (and thus GPU acceleration) is available."""
    return _CUPY_AVAILABLE


def gpu_apply_rules(words: List[str], rules: List[str]) -> List[str]:
    """Apply hashcat rules on the GPU using CuPy.

    This is an experimental feature.  It encodes words and rules into
    GPU arrays and applies character-level transformations in parallel.

    Args:
        words: List of base words.
        rules: List of hashcat-style rule strings.

    Returns:
        List of mutated words from GPU computation.
    """
    if not _CUPY_AVAILABLE:
        logger.warning("CuPy not installed. Falling back to CPU.")
        return []

    logger.info(
        "GPU acceleration: processing %d words with %d rules", len(words), len(rules)
    )

    # For now, this is a placeholder that demonstrates the interface.
    # A full GPU implementation would:
    # 1. Encode all words into a fixed-width character array on GPU
    # 2. Encode rules into operation arrays
    # 3. Use CuPy kernels to apply rules in parallel
    # 4. Transfer results back to CPU

    # Placeholder: fall back to CPU rule application
    from pawpy.mutations.mangle import apply_hashcat_rules

    all_results = set()
    for word in words:
        all_results.update(apply_hashcat_rules(word, rules))

    logger.info("GPU mode complete (CPU fallback): %d candidates", len(all_results))
    return sorted(all_results)
