"""zxcvbn-based password strength scoring and pruning."""

from __future__ import annotations

import logging
from typing import List, Optional

logger = logging.getLogger("pawpy.scorer")

_zxcvbn_available = False
try:
    from zxcvbn import zxcvbn

    _zxcvbn_available = True
except ImportError:
    zxcvbn = None  # type: ignore[assignment, misc]


def is_zxcvbn_available() -> bool:
    """Check whether zxcvbn library is installed."""
    return _zxcvbn_available


def score_password(password: str) -> Optional[int]:
    """Score a password using zxcvbn.

    Returns:
        An integer score 0-4, or None if zxcvbn is not available.
        0 = very weak, 4 = very strong.
    """
    if not _zxcvbn_available:
        return None
    try:
        result = zxcvbn(password)
        return result.get("score", 0)
    except Exception:
        logger.debug("zxcvbn failed on: %s", password[:20])
        return None


def score_and_prune(candidates: List[str], min_score: int) -> List[str]:
    """Filter candidates to those with zxcvbn score >= *min_score*.

    If zxcvbn is not available, returns all candidates unchanged.
    """
    if not _zxcvbn_available:
        logger.warning("zxcvbn not installed – skipping strength scoring.")
        return candidates

    min_score = max(0, min(min_score, 4))
    kept = []
    pruned = 0
    for candidate in candidates:
        score = score_password(candidate)
        if score is not None and score < min_score:
            pruned += 1
            continue
        kept.append(candidate)

    logger.info(
        "zxcvbn scoring: kept %d, pruned %d (min_score=%d)",
        len(kept),
        pruned,
        min_score,
    )
    return kept
