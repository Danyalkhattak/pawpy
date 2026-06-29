"""Main pipeline orchestrator – coordinates all mutation and output stages."""

from __future__ import annotations

import logging
import os
from datetime import datetime
from typing import Any, Dict, List, Optional, Set

from rich.console import Console

from pawpy.config import PawpyConfig
from pawpy.generator.hybrid import hybrid_generate
from pawpy.mutations.dates import date_permutations
from pawpy.mutations.keyboard import dynamic_keyboard_walks, static_keyboard_walks
from pawpy.mutations.leet import leet_speak
from pawpy.mutations.mangle import apply_hashcat_rules, load_rules_file, mangle_rules
from pawpy.mutations.markov import generate_markov_words
from pawpy.mutations.templates import expand_templates
from pawpy.utils import make_progress

console = Console()
logger = logging.getLogger("pawpy.generator")


class PipelineOrchestrator:
    """Orchestrates the full password generation pipeline.

    Stages:
    1. Collect base words + dates from profile
    2. Generate mutations (leet, mangle, dates, keyboard, templates, rules, Markov, hybrid, year blends)
    3. Merge common passwords
    4. Optional scoring & policy filtering
    5. Sort and deduplicate
    6. Write output
    """

    def __init__(self, config: PawpyConfig, profile: Dict[str, Any]) -> None:
        self.config = config
        self.profile = profile
        self._candidates: Set[str] = set()
        self._temp_dir: Optional[str] = None

    def _get_base_words(self) -> List[str]:
        """Extract base words from the profile."""
        # Handle both single-profile and merged multi-profile formats
        list_fields = {"children", "keywords"}
        words: Set[str] = set()
        for key, value in self.profile.items():
            if key in list_fields:
                if isinstance(value, list):
                    for item in value:
                        if isinstance(item, str) and item.strip():
                            words.add(item.strip().lower())
                elif isinstance(value, str):
                    for item in value.split(","):
                        if item.strip():
                            words.add(item.strip().lower())
            else:
                if isinstance(value, str) and value.strip():
                    words.add(value.strip().lower())
                elif isinstance(value, list):
                    for item in value:
                        if isinstance(item, str) and item.strip():
                            words.add(item.strip().lower())
        return sorted(words)

    def _get_dates(self) -> List[str]:
        """Extract date strings from the profile."""
        dates = set()
        for field in ("birthdate", "partner_bdate"):
            val = self.profile.get(field, "")
            if isinstance(val, str) and val.strip():
                dates.add(val.strip())
            elif isinstance(val, list):
                for d in val:
                    if isinstance(d, str) and d.strip():
                        dates.add(d.strip())
        return sorted(dates)

    def _add_candidates(self, candidates: List[str]) -> int:
        """Add candidates to the in-memory set, switching to disk if needed."""
        new = 0
        for c in candidates:
            if c and c not in self._candidates:
                self._candidates.add(c)
                new += 1
        return new

    def _year_blend(self, word: str) -> List[str]:
        """Append/prepend years 1990..current year to a word."""
        current_year = datetime.now().year
        results = []
        for year in range(1990, current_year + 1):
            results.append(f"{word}{year}")
            results.append(f"{word}{str(year)[-2:]}")
            results.append(f"{year}{word}")
            results.append(f"{str(year)[-2:]}{word}")
        return results

    def _two_word_combos(self, words: List[str]) -> List[str]:
        """Generate two-word combinations with separators."""
        if len(words) > 30:
            words = words[:30]  # cap to prevent explosion
        separators = ["", "_", "-", ".", "@", "#", "!", " "]
        results = []
        for i, w1 in enumerate(words):
            for w2 in words[i + 1 :]:
                for sep in separators:
                    results.append(f"{w1}{sep}{w2}")
                    results.append(f"{w1}{sep}{w2.capitalize()}")
                    results.append(f"{w1.capitalize()}{sep}{w2}")
                    results.append(f"{w1.capitalize()}{sep}{w2.capitalize()}")
        return results

    def run(self) -> str:
        """Execute the full pipeline. Returns the output file path."""
        progress = make_progress()
        total_added = 0

        # --- Stage 1: Base words ---
        base_words = self._get_base_words()
        dates = self._get_dates()
        logger.info("Base words: %d, Dates: %d", len(base_words), len(dates))

        task_base = progress.add_task("[cyan]Collecting base words...", total=None)
        self._add_candidates(base_words)
        self._add_candidates([w.capitalize() for w in base_words])
        self._add_candidates([w.upper() for w in base_words])
        total_added += len(self._candidates)
        progress.update(task_base, completed=True)

        # --- Stage 2: Date permutations ---
        task_dates = progress.add_task("[cyan]Date permutations...", total=None)
        date_frags = []
        for d in dates:
            date_frags.extend(date_permutations(d))
        self._add_candidates(date_frags)
        # Combine dates with base words
        for word in base_words:
            for frag in date_frags[:20]:  # limit to prevent explosion
                self._candidates.add(f"{word}{frag}")
                self._candidates.add(f"{frag}{word}")
        progress.update(task_dates, completed=True)

        # --- Stage 3: Leet speak ---

        leet_variants = []
        for word in base_words:
            leet_variants.extend(leet_speak(word, level=2))
        self._add_candidates(leet_variants)
        progress.update(task_dates, completed=True)

        # --- Stage 4: Common mangle rules ---
        task_mangle = progress.add_task("[cyan]Common mangle rules...", total=None)
        mangled = []
        for word in base_words:
            mangled.extend(mangle_rules(word))
        self._add_candidates(mangled)
        progress.update(task_mangle, completed=True)

        # --- Stage 5: Keyboard walks ---
        task_kb = progress.add_task("[cyan]Keyboard walks...", total=None)
        self._add_candidates(static_keyboard_walks())
        if self.config.is_extreme and not self.config.is_lite:
            walks = dynamic_keyboard_walks(min_len=4, max_len=6)
            self._add_candidates(walks)
        progress.update(task_kb, completed=True)

        # --- Stage 6: Hashcat rules ---
        if self.config.rule_file:
            task_rules = progress.add_task(
                "[cyan]Applying hashcat rules...", total=None
            )
            rules = load_rules_file(self.config.rule_file)
            for word in base_words:
                self._add_candidates(apply_hashcat_rules(word, rules))
            progress.update(task_rules, completed=True)

        # --- Stage 7: Custom templates ---
        if self.config.templates:
            task_tmpl = progress.add_task("[cyan]Expanding templates...", total=None)
            expanded = expand_templates(self.config.templates, self.profile)
            self._add_candidates(expanded)
            progress.update(task_tmpl, completed=True)

        # --- Stage 8: Markov blending ---
        if self.config.markov and not self.config.is_lite:
            task_markov = progress.add_task("[cyan]Markov blending...", total=None)
            # Use base words + common passwords as training corpus
            from pawpy.data.common_passwords import TOP_10K

            corpus = base_words + TOP_10K[:2000]
            markov_words = generate_markov_words(
                corpus,
                count=self.config.markov_count,
                order=self.config.markov_order,
            )
            self._add_candidates(markov_words)
            progress.update(task_markov, completed=True)

        # --- Stage 9: Year-word blends ---
        if self.config.is_extreme or not self.config.is_lite:
            task_years = progress.add_task("[cyan]Year-word blends...", total=None)
            year_blends = []
            for word in base_words:
                year_blends.extend(self._year_blend(word))
            self._add_candidates(year_blends)
            progress.update(task_years, completed=True)

        # --- Stage 10: Two-word combinations ---
        if not self.config.is_lite:
            task_combo = progress.add_task("[cyan]Two-word combinations...", total=None)
            combos = self._two_word_combos(base_words)
            self._add_candidates(combos)
            progress.update(task_combo, completed=True)

        # --- Stage 11: Hybrid attacks ---
        if self.config.hybrid_left or self.config.hybrid_right:
            task_hybrid = progress.add_task("[cyan]Hybrid mask attacks...", total=None)
            hybrid_cands = hybrid_generate(
                base_words,
                left_mask=self.config.hybrid_left,
                right_mask=self.config.hybrid_right,
            )
            self._add_candidates(hybrid_cands)
            progress.update(task_hybrid, completed=True)

        # --- Stage 12: Common passwords ---
        task_common = progress.add_task("[cyan]Merging common passwords...", total=None)
        from pawpy.data.common_passwords import TOP_10K

        self._add_candidates(TOP_10K)
        progress.update(task_common, completed=True)

        progress.stop()
        console.print(
            f"\n[green]✓[/green] Total candidates before filtering: [bold]{len(self._candidates):,}[/bold]"
        )

        # --- Stage 13: Scoring & Filtering ---
        candidates_list = list(self._candidates)

        if self.config.min_strength is not None:
            from pawpy.scoring.scorer import score_and_prune

            task_score = progress.add_task("[cyan]Scoring passwords...", total=None)
            candidates_list = score_and_prune(candidates_list, self.config.min_strength)
            progress.update(task_score, completed=True)
            progress.stop()
            console.print(
                f"[green]✓[/green] After scoring: [bold]{len(candidates_list):,}[/bold]"
            )

        if any(
            [
                self.config.min_length,
                self.config.require_upper,
                self.config.require_lower,
                self.config.require_digit,
                self.config.require_special,
            ]
        ):
            from pawpy.filters.policy import PolicyFilter

            pf = PolicyFilter(
                min_length=self.config.min_length,
                require_upper=self.config.require_upper,
                require_lower=self.config.require_lower,
                require_digit=self.config.require_digit,
                require_special=self.config.require_special,
            )
            task_policy = progress.add_task(
                "[cyan]Applying policy filter...", total=None
            )
            candidates_list = [c for c in candidates_list if pf.check(c)]
            progress.update(task_policy, completed=True)
            progress.stop()
            console.print(
                f"[green]✓[/green] After policy filter: [bold]{len(candidates_list):,}[/bold]"
            )

        # --- Stage 14: Sort & Dedup ---
        candidates_list.sort()
        # Remove duplicates (shouldn't be needed but safety)
        seen = set()
        unique = []
        for c in candidates_list:
            if c not in seen:
                seen.add(c)
                unique.append(c)
        candidates_list = unique

        # --- Stage 15: Write output ---
        output_path = self.config.output_file
        task_write = progress.add_task(
            "[cyan]Writing wordlist...", total=len(candidates_list)
        )
        with open(output_path, "w", encoding="utf-8") as fh:
            for i, word in enumerate(candidates_list):
                fh.write(word + "\n")
                if i % 100_000 == 0:
                    progress.update(task_write, completed=i)
        progress.update(task_write, completed=len(candidates_list))
        progress.stop()

        size_mb = os.path.getsize(output_path) / (1024 * 1024)
        console.print(
            f"\n[bold green]✓ Wordlist generated![/bold green]\n"
            f"  File:     [cyan]{output_path}[/cyan]\n"
            f"  Entries:  [bold]{len(candidates_list):,}[/bold]\n"
            f"  Size:     [bold]{size_mb:.2f} MB[/bold]\n"
        )
        return output_path
