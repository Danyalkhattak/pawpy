"""Embedded top common passwords list.

This module contains a curated list of the most common passwords derived
from publicly available breach data (SecLists).  The full 10,000-entry
list can be downloaded via ``pawpy update-passwords`` which fetches the
latest version from the SecLists repository.

Only the top 100 entries are embedded here to keep the package size
reasonable.  The updater stores the full list alongside this file.
"""

from __future__ import annotations

from pathlib import Path
from typing import List

# Top 100 most common passwords (from public breach analyses)
TOP_10K: List[str] = [
    "123456",
    "password",
    "12345678",
    "qwerty",
    "123456789",
    "12345",
    "1234",
    "111111",
    "1234567",
    "dragon",
    "123123",
    "baseball",
    "abc123",
    "football",
    "monkey",
    "letmein",
    "696969",
    "shadow",
    "master",
    "666666",
    "qwertyuiop",
    "123321",
    "mustang",
    "1234567890",
    "michael",
    "654321",
    "pussy",
    "superman",
    "1qaz2wsx",
    "7777777",
    "fuckyou",
    "121212",
    "000000",
    "qazwsx",
    "123qwe",
    "killer",
    "trustno1",
    "jordan",
    "jennifer",
    "zxcvbnm",
    "asdfgh",
    "hunter",
    "buster",
    "soccer",
    "harley",
    "batman",
    "andrew",
    "tigger",
    "sunshine",
    "iloveyou",
    "fuckme",
    "2000",
    "charlie",
    "robert",
    "thomas",
    "hockey",
    "ranger",
    "daniel",
    "starwars",
    "klaster",
    "112233",
    "george",
    "asshole",
    "computer",
    "michelle",
    "jessica",
    "pepper",
    "1111",
    "zxcvbn",
    "555555",
    "131313",
    "freedom",
    "777777",
    "pass",
    "fuck",
    "maggie",
    "159753",
    "aaaaaa",
    "ginger",
    "princess",
    "joshua",
    "cheese",
    "amanda",
    "summer",
    "love",
    "ashley",
    "6969",
    "nicole",
    "chelsea",
    "biteme",
    "matthew",
    "access",
    "yankees",
    "987654321",
    "dallas",
    "austin",
    "thunder",
    "taylor",
    "matrix",
]

# Path where the updater stores the full SecLists top passwords
_SECLISTS_CACHE = Path(__file__).parent / "_seclists_top10k.txt"


def get_common_passwords() -> List[str]:
    """Return the common passwords list.

    If the full SecLists file has been downloaded (via ``pawpy update-passwords``),
    it is used instead of the embedded top-100.
    """
    if _SECLISTS_CACHE.exists():
        passwords = []
        with open(_SECLISTS_CACHE, "r", encoding="utf-8", errors="ignore") as fh:
            for line in fh:
                stripped = line.strip()
                if stripped:
                    passwords.append(stripped)
        if passwords:
            return passwords
    return TOP_10K
