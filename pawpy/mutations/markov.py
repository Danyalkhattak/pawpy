"""Markov chain-based password generation.

Trains a character-level Markov model on a corpus of words and
generates new candidate passwords that follow similar patterns.
"""

from __future__ import annotations

import logging
import random
from collections import defaultdict
from typing import Dict, List, Optional

logger = logging.getLogger("pawpy.markov")


class MarkovModel:
    """Character-level Markov chain for password generation.

    The model records the probability of each character following a
    sequence of *order* previous characters.  Generation starts from
    a random seed and follows the chain until a stop condition.
    """

    def __init__(self, order: int = 2) -> None:
        self.order = order
        # transition_table[context][next_char] = count
        self.transition_table: Dict[str, Dict[str, int]] = defaultdict(
            lambda: defaultdict(int)
        )
        self.total_chars = 0

    def train(self, words: List[str]) -> None:
        """Train the model on a list of words."""
        for word in words:
            w = word.lower().strip()
            if not w:
                continue
            # Pad start and end
            padded = "^" * self.order + w + "$"
            for i in range(len(padded) - self.order):
                context = padded[i : i + self.order]
                next_char = padded[i + self.order]
                self.transition_table[context][next_char] += 1
                self.total_chars += 1

        logger.debug(
            "Markov model trained: order=%d, contexts=%d, total_chars=%d",
            self.order,
            len(self.transition_table),
            self.total_chars,
        )

    def generate(self, min_len: int = 6, max_len: int = 16) -> Optional[str]:
        """Generate a single password from the trained model."""
        if not self.transition_table:
            return None

        # Start from a random context
        contexts = [ctx for ctx in self.transition_table if all(c == "^" for c in ctx)]
        if not contexts:
            return None

        context = random.choice(contexts)
        result = ""

        for _ in range(max_len):
            if context not in self.transition_table:
                break
            next_chars = self.transition_table[context]
            if not next_chars:
                break

            # Weighted random choice
            total = sum(next_chars.values())
            r = random.randint(1, total)
            cumulative = 0
            chosen = "$"  # default: end
            for ch, count in next_chars.items():
                cumulative += count
                if cumulative >= r:
                    chosen = ch
                    break

            if chosen == "$":
                break
            result += chosen
            context = context[1:] + chosen

        if len(result) < min_len:
            return None
        return result

    def generate_many(
        self, count: int, min_len: int = 6, max_len: int = 16
    ) -> List[str]:
        """Generate *count* unique passwords."""
        results: set = set()
        attempts = 0
        max_attempts = count * 10
        while len(results) < count and attempts < max_attempts:
            word = self.generate(min_len, max_len)
            if word:
                results.add(word)
            attempts += 1
        return sorted(results)


def train_markov(words: List[str], order: int = 2) -> MarkovModel:
    """Convenience function: create, train, and return a MarkovModel."""
    model = MarkovModel(order=order)
    model.train(words)
    return model


def generate_markov_words(
    words: List[str],
    count: int = 5000,
    order: int = 2,
    min_len: int = 6,
    max_len: int = 16,
) -> List[str]:
    """Train a Markov model on *words* and generate *count* candidates."""
    model = train_markov(words, order=order)
    return model.generate_many(count, min_len, max_len)
