"""Profile collector – interactive (CUPP-style) and JSON import."""

from __future__ import annotations

import json
import logging
from typing import Any, Dict, List

from rich.console import Console

console = Console()
logger = logging.getLogger("pawpy.profile")


class ProfileCollector:
    """Collect target profile data interactively or from JSON."""

    # Standard fields expected in a profile
    FIELDS = [
        "firstname",
        "lastname",
        "nickname",
        "birthdate",
        "partner",
        "partner_nick",
        "partner_bdate",
        "pet",
        "company",
        "hometown",
        "favourite_color",
    ]
    LIST_FIELDS = ["children", "keywords"]

    def __init__(self) -> None:
        self._profile: Dict[str, Any] = {k: "" for k in self.FIELDS}
        self._profile["children"] = []
        self._profile["keywords"] = []

    # ------------------------------------------------------------------
    # Interactive collection
    # ------------------------------------------------------------------

    def interactive_collect(self) -> Dict[str, Any]:
        """Present a CUPP-style questionnaire and return the profile dict."""
        console.print("\n[bold cyan]── Target Profile Collection ──[/bold cyan]\n")

        prompts = {
            "firstname": ("First name", "John"),
            "lastname": ("Last name", "Doe"),
            "nickname": ("Nickname", "Johnny"),
            "birthdate": ("Birthdate (DDMMYYYY)", "01011990"),
            "partner": ("Partner's first name", ""),
            "partner_nick": ("Partner's nickname", ""),
            "partner_bdate": ("Partner's birthdate (DDMMYYYY)", ""),
            "pet": ("Pet's name", ""),
            "company": ("Company / organisation", ""),
            "hometown": ("City / hometown", ""),
            "favourite_color": ("Favourite colour", ""),
        }

        for field, (label, example) in prompts.items():
            answer = console.input(
                f"  [dim]{label}[/dim] [dim](e.g. {example})[/dim]: "
            ).strip()
            self._profile[field] = answer

        children_raw = console.input(
            "  [dim]Children's names (comma-separated)[/dim]: "
        ).strip()
        self._profile["children"] = [
            c.strip() for c in children_raw.split(",") if c.strip()
        ]

        keywords_raw = console.input(
            "  [dim]Keywords / interests (comma-separated)[/dim]: "
        ).strip()
        self._profile["keywords"] = [
            k.strip() for k in keywords_raw.split(",") if k.strip()
        ]

        console.print()
        return self._profile

    # ------------------------------------------------------------------
    # JSON import
    # ------------------------------------------------------------------

    @staticmethod
    def from_json(path: str) -> Dict[str, Any]:
        """Load a single profile from a JSON file.

        Raises ``ValueError`` if the file contains a JSON array (use
        ``--multi`` for arrays).
        """
        with open(path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        if isinstance(data, list):
            raise ValueError(
                f"File '{path}' contains a JSON array of profiles. "
                "Use --multi to import multiple profiles."
            )
        return data

    # ------------------------------------------------------------------
    # Word / date extraction
    # ------------------------------------------------------------------

    @staticmethod
    def extract_base_words(profile: Dict[str, Any]) -> List[str]:
        """Extract all non-empty text values from a profile as lowercase words.

        String fields yield one word each; list fields yield one word per
        element.  The result is deduplicated and sorted.
        """
        words: set = set()
        list_fields = {"children", "keywords"}
        for key, value in profile.items():
            if key in list_fields:
                if isinstance(value, list):
                    for item in value:
                        if isinstance(item, str) and item.strip():
                            words.add(item.strip().lower())
            else:
                if isinstance(value, str) and value.strip():
                    words.add(value.strip().lower())
        return sorted(words)

    @staticmethod
    def extract_dates(profile: Dict[str, Any]) -> List[str]:
        """Return date strings found in the profile (birthdate, partner_bdate)."""
        dates = []
        for field in ("birthdate", "partner_bdate"):
            val = profile.get(field, "")
            if isinstance(val, str) and val.strip():
                dates.append(val.strip())
        return dates

    # ------------------------------------------------------------------
    # Main entry point
    # ------------------------------------------------------------------

    def run(self, config) -> Dict[str, Any]:
        """Collect profile based on configuration.

        If *config.profile_json* is set, load from file; otherwise
        run the interactive questionnaire.  Optionally run OSINT plugins.
        """
        from pawpy.profile.plugins import run_plugins  # lazy import

        if config.profile_json:
            self._profile = self.from_json(config.profile_json)
            console.print(
                f"[green]✓[/green] Loaded profile from [bold]{config.profile_json}[/bold]"
            )
        else:
            self._profile = self.interactive_collect()

        # Run OSINT plugins if any are installed
        self._profile = run_plugins(self._profile)

        return self._profile
