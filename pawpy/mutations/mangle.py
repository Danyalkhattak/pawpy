"""Common mangle rules and Hashcat/John-style rule engine."""

from __future__ import annotations

import logging
import re
from typing import List, Optional

logger = logging.getLogger("pawpy.mangle")

# Common append/prepend strings
APPENDS = [
    "",
    "1",
    "2",
    "3",
    "12",
    "13",
    "21",
    "22",
    "23",
    "99",
    "123",
    "1234",
    "!",
    "@",
    "#",
    "$",
    "!!",
    "!@#",
    "01",
    "69",
    "!",
    "?",
    "*",
    ".",
    "_",
    "-",
    "@1",
    "@123",
    "#1",
]
PREPENDS = ["", "1", "123", "!", "@", "#", "$", "?", "*"]


def mangle_rules(word: str) -> List[str]:
    """Apply common mangle rules: capitalise, upper, reverse, append, prepend.

    Returns a list of mutated variants (always includes the original).
    """
    results = set()
    results.add(word)
    results.add(word.capitalize())
    results.add(word.upper())
    results.add(word.lower())
    results.add(word[::-1])  # reverse
    results.add(word.swapcase())
    results.add(word[0].upper() + word[1:].lower() if word else word)
    # toggle first and last case
    if len(word) > 1:
        results.add(word[0].upper() + word[1:-1] + word[-1].upper())

    for suffix in APPENDS:
        results.add(word + suffix)
        results.add(word.capitalize() + suffix)

    for prefix in PREPENDS:
        if prefix:  # skip empty prefix (already have original)
            results.add(prefix + word)
            results.add(prefix + word.capitalize())

    return sorted(results)


# ---------------------------------------------------------------------------
# Hashcat / John the Ripper rule engine
# ---------------------------------------------------------------------------


def _apply_rule(word: str, rule: str) -> Optional[str]:
    """Apply a single hashcat-style rule to *word*.

    Supported rules (subset of hashcat):
    - Lowercase:  l  /  : (legacy)
    - Uppercase:  u
    - Capitalise: c  (first char upper, rest lower)
    - Swap case:  s
    - Reverse:    r
    - Append:     $X  (append char X)
    - Prepend:    ^X  (prepend char X)
    - Truncate left:  [N  (keep first N chars)
    - Truncate right: ]N  (keep last N chars)
    - Insert at pos:  iNX  (insert char X at position N)
    - Overwrite at pos: oNX  (overwrite char at position N with X)
    - Duplicate:  d
    - Duplicate first: p
    - Duplicate last:  z
    - Replace:    sXY  (replace all X with Y)
    """
    w = list(word)

    i = 0
    while i < len(rule):
        cmd = rule[i]

        if cmd == "l":
            w = [c.lower() for c in w]
            i += 1
        elif cmd == "u":
            w = [c.upper() for c in w]
            i += 1
        elif cmd == "c":
            if w:
                w = [w[0].upper()] + [c.lower() for c in w[1:]]
            i += 1
        elif cmd == "s":
            w = [c.swapcase() for c in w]
            i += 1
        elif cmd == "r":
            w = w[::-1]
            i += 1
        elif cmd == "d":
            w = w + w
            i += 1
        elif cmd == "p":
            if w:
                w = [w[0]] + w
            i += 1
        elif cmd == "z":
            if w:
                w = w + [w[-1]]
            i += 1
        elif cmd == "$":
            # Append next char
            if i + 1 < len(rule):
                w.append(rule[i + 1])
                i += 2
            else:
                i += 1
        elif cmd == "^":
            # Prepend next char
            if i + 1 < len(rule):
                w.insert(0, rule[i + 1])
                i += 2
            else:
                i += 1
        elif cmd == "[":
            # Truncate from left – keep first N
            m = re.match(r"\[(\d+)", rule[i:])
            if m:
                n = int(m.group(1))
                w = w[:n]
                i += 1 + len(m.group(1))
            else:
                i += 1
        elif cmd == "]":
            # Truncate from right – keep last N
            m = re.match(r"\](\d+)", rule[i:])
            if m:
                n = int(m.group(1))
                w = w[-n:] if n > 0 else []
                i += 1 + len(m.group(1))
            else:
                i += 1
        elif cmd == "i":
            # Insert char X at position N: iNX
            m = re.match(r"i(\d+)(.)", rule[i:])
            if m:
                pos = int(m.group(1))
                ch = m.group(2)
                if pos <= len(w):
                    w.insert(pos, ch)
                i += 1 + len(m.group(1)) + 1
            else:
                i += 1
        elif cmd == "o":
            # Overwrite char at position N with X: oNX
            m = re.match(r"o(\d+)(.)", rule[i:])
            if m:
                pos = int(m.group(1))
                ch = m.group(2)
                if 0 <= pos < len(w):
                    w[pos] = ch
                i += 1 + len(m.group(1)) + 1
            else:
                i += 1
        elif cmd == "'":
            # Replace all X with Y: sXY (or 'XY in john format)
            if i + 2 < len(rule):
                old_ch = rule[i + 1]
                new_ch = rule[i + 2]
                w = [new_ch if c == old_ch else c for c in w]
                i += 3
            else:
                i += 1
        else:
            # Unknown rule – skip
            i += 1

    return "".join(w)


def apply_hashcat_rules(word: str, rules: List[str]) -> List[str]:
    """Apply a list of hashcat-style rules to *word*.

    Each rule string may contain multiple rule commands (applied left to
    right).  Returns the list of results.

    Args:
        word: The base word.
        rules: A list of rule strings, one per line (as read from a .rule file).

    Returns:
        List of mutated words. Empty results are excluded.
    """
    results = set()
    for rule in rules:
        rule = rule.strip()
        if not rule or rule.startswith("#"):
            continue
        try:
            mutated = _apply_rule(word, rule)
            if mutated:
                results.add(mutated)
        except Exception:
            logger.debug("Failed to apply rule '%s' to '%s'", rule, word)
    return sorted(results)


def load_rules_file(path: str) -> List[str]:
    """Load rules from a hashcat .rule file (one rule per line)."""
    rules = []
    with open(path, "r", encoding="utf-8", errors="ignore") as fh:
        for line in fh:
            stripped = line.strip()
            if stripped and not stripped.startswith("#"):
                rules.append(stripped)
    return rules
