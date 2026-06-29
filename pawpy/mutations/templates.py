"""Custom pattern template engine.

Expands templates like ``[FirstName][Year][Special]`` by substituting
profile fields and generating combinatorial expansions.
"""

from __future__ import annotations

import re
from datetime import datetime
from typing import Any, Dict, List

# Recognised template tokens (inside [brackets])
_TOKEN_RE = re.compile(r"\[([A-Za-z_]+)\]")

# Special character sets used by some tokens
_SPECIALS = ["!", "@", "#", "$", "%", "^", "&", "*", "?", ".", "_", "-"]
_DIGITS = [str(i) for i in range(10)]

# Current year
_CURRENT_YEAR = datetime.now().year


def _resolve_token(token: str, profile: Dict[str, Any]) -> List[str]:
    """Resolve a single template token to a list of possible values."""
    t = token.lower()

    # Direct profile fields
    field_map = {
        "firstname": "firstname",
        "lastname": "lastname",
        "nickname": "nickname",
        "partner": "partner",
        "partner_nick": "partner_nick",
        "pet": "pet",
        "company": "company",
        "hometown": "hometown",
        "color": "favourite_color",
        "favourite_color": "favourite_color",
    }
    if t in field_map:
        val = profile.get(field_map[t], "")
        if isinstance(val, str) and val.strip():
            return [val, val.capitalize(), val.upper(), val.lower()]
        return []

    # Date-related tokens
    if t in ("year", "yr"):
        return [str(_CURRENT_YEAR - i) for i in range(40)]  # 1986..current
    if t in ("year2", "yr2"):
        return [str(y)[-2:] for y in range(_CURRENT_YEAR - 40, _CURRENT_YEAR + 1)]
    if t == "date":
        bd = profile.get("birthdate", "")
        return [bd] if isinstance(bd, str) and bd.strip() else []

    # Character class tokens
    if t == "digit":
        return _DIGITS
    if t in ("special", "spec", "sym"):
        return _SPECIALS
    if t == "upper":
        return [chr(c) for c in range(ord("A"), ord("Z") + 1)]
    if t == "lower":
        return [chr(c) for c in range(ord("a"), ord("z") + 1)]

    # Children / keywords
    if t in ("child", "children"):
        val = profile.get("children", [])
        if isinstance(val, list):
            return [c for c in val if isinstance(c, str) and c.strip()]
        return []
    if t == "keyword" or t == "keywords":
        val = profile.get("keywords", [])
        if isinstance(val, list):
            return [k for k in val if isinstance(k, str) and k.strip()]
        return []

    # Static tokens
    if t == "sep":
        return ["_", "-", ".", "", "@", "#"]
    if t == "123":
        return ["123", "1234", "12345", "!@#", "1q2w3e"]

    return []


def expand_templates(
    templates: List[str],
    profile: Dict[str, Any],
    max_combinations: int = 100_000,
) -> List[str]:
    """Expand a list of template strings using profile data.

    Each template may contain ``[Token]`` placeholders which are resolved
    via ``_resolve_token``.  All combinations are generated.

    Args:
        templates: List of template strings like ``[FirstName][Year][!]``.
        profile: Target profile dictionary.
        max_combinations: Safety limit on total output size.

    Returns:
        List of expanded password candidates.
    """
    results = []
    total = 0

    for tmpl in templates:
        # Find all tokens in order
        tokens = _TOKEN_RE.findall(tmpl)
        if not tokens:
            results.append(tmpl)
            continue

        # Resolve each token to its possible values
        token_values = [_resolve_token(tok, profile) for tok in tokens]

        # Cartesian product
        import itertools

        for combo in itertools.product(*token_values):
            if total >= max_combinations:
                return results
            candidate = tmpl
            for tok, val in zip(tokens, combo):
                candidate = candidate.replace(f"[{tok}]", val, 1)
                candidate = candidate.replace(f"[{tok.lower()}]", val, 1)
            results.append(candidate)
            total += 1

    return results
