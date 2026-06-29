"""Tests for keyboard walk generation."""

from pawpy.mutations.keyboard import static_keyboard_walks


def test_static_walks_not_empty():
    walks = static_keyboard_walks()
    assert len(walks) > 0


def test_static_walks_contains_qwerty():
    walks = static_keyboard_walks()
    assert "qwerty" in walks


def test_static_walks_contains_asdf():
    walks = static_keyboard_walks()
    assert "asdf" in walks
