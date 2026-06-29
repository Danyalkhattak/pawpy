"""Mutation engine – transforms base words into password candidates."""

from pawpy.mutations.dates import date_permutations
from pawpy.mutations.keyboard import dynamic_keyboard_walks, static_keyboard_walks
from pawpy.mutations.leet import leet_speak
from pawpy.mutations.mangle import apply_hashcat_rules, mangle_rules
from pawpy.mutations.markov import generate_markov_words, train_markov
from pawpy.mutations.templates import expand_templates

__all__ = [
    "leet_speak",
    "date_permutations",
    "mangle_rules",
    "apply_hashcat_rules",
    "static_keyboard_walks",
    "dynamic_keyboard_walks",
    "train_markov",
    "generate_markov_words",
    "expand_templates",
]
