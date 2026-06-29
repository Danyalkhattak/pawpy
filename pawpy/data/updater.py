"""Auto-update utility for common password lists.

Downloads the latest top passwords from the SecLists repository.
"""

from __future__ import annotations

import logging
import urllib.request
from pathlib import Path
from typing import Optional

logger = logging.getLogger("pawpy.updater")

_SECLISTS_URL = (
    "https://raw.githubusercontent.com/danielmiessler/SecLists/"
    "master/Passwords/Common-Credentials/10k-most-common.txt"
)
_CACHE_PATH = Path(__file__).parent / "_seclists_top10k.txt"


def update_common_passwords(
    url: Optional[str] = None, output: Optional[str] = None
) -> str:
    """Download the latest common passwords list from SecLists.

    Args:
        url: Override URL (default: SecLists 10k-most-common.txt).
        output: Override output path (default: alongside this module).

    Returns:
        Path to the downloaded file.
    """
    url = url or _SECLISTS_URL
    output_path = Path(output) if output else _CACHE_PATH

    logger.info("Downloading common passwords from: %s", url)
    try:
        urllib.request.urlretrieve(url, output_path)
        # Count lines
        count = 0
        with open(output_path, "r", encoding="utf-8", errors="ignore") as fh:
            for _ in fh:
                count += 1
        logger.info("Downloaded %d passwords to %s", count, output_path)
        return str(output_path)
    except Exception as e:
        logger.error("Failed to download: %s", e)
        raise
