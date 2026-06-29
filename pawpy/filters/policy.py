"""Password complexity policy filter.

Enforces common password policy requirements such as minimum length
and character class requirements.
"""

from __future__ import annotations

import re
from typing import Optional


class PolicyFilter:
    """Check whether a password meets a given complexity policy.

    All checks are optional – only enabled checks are enforced.
    """

    def __init__(
        self,
        min_length: Optional[int] = None,
        require_upper: bool = False,
        require_lower: bool = False,
        require_digit: bool = False,
        require_special: bool = False,
    ) -> None:
        self.min_length = min_length
        self.require_upper = require_upper
        self.require_lower = require_lower
        self.require_digit = require_digit
        self.require_special = require_special

    def check(self, password: str) -> bool:
        """Return True if *password* passes all enabled policy checks."""
        if self.min_length is not None and len(password) < self.min_length:
            return False
        if self.require_upper and not re.search(r"[A-Z]", password):
            return False
        if self.require_lower and not re.search(r"[a-z]", password):
            return False
        if self.require_digit and not re.search(r"[0-9]", password):
            return False
        if self.require_special and not re.search(r"[^A-Za-z0-9]", password):
            return False
        return True

    def __repr__(self) -> str:
        checks = []
        if self.min_length:
            checks.append(f"min_len={self.min_length}")
        if self.require_upper:
            checks.append("upper")
        if self.require_lower:
            checks.append("lower")
        if self.require_digit:
            checks.append("digit")
        if self.require_special:
            checks.append("special")
        return f"PolicyFilter({', '.join(checks)})"
