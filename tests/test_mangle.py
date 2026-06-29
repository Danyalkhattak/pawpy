"""Tests for mangle rules and hashcat rule engine."""

from pawpy.mutations.mangle import _apply_rule, apply_hashcat_rules, mangle_rules


def test_mangle_includes_original():
    result = mangle_rules("password")
    assert "password" in result


def test_mangle_capitalize():
    result = mangle_rules("password")
    assert "Password" in result


def test_mangle_upper():
    result = mangle_rules("password")
    assert "PASSWORD" in result


def test_mangle_reverse():
    result = mangle_rules("password")
    assert "drowssap" in result


def test_mangle_append():
    result = mangle_rules("pass")
    assert "pass123" in result
    assert "pass!" in result


def test_hashcat_rule_lower():
    assert _apply_rule("HELLO", "l") == "hello"


def test_hashcat_rule_upper():
    assert _apply_rule("hello", "u") == "HELLO"


def test_hashcat_rule_capitalize():
    assert _apply_rule("hello world", "c") == "Hello world"


def test_hashcat_rule_reverse():
    assert _apply_rule("abc", "r") == "cba"


def test_hashcat_rule_append():
    assert _apply_rule("pass", "$!") == "pass!"


def test_hashcat_rule_prepend():
    assert _apply_rule("pass", "^!") == "!pass"


def test_hashcat_rule_duplicate():
    assert _apply_rule("ab", "d") == "abab"


def test_hashcat_rule_truncate():
    assert _apply_rule("hello", "[3") == "hel"


def test_hashcat_rule_replace():
    # 'XY in John format replaces all X with Y (single char each)
    assert _apply_rule("abab", "'ab") == "bbbb"
    assert _apply_rule("abab", "'ac") == "cbcb"


def test_apply_rules_list():
    # Each rule is applied independently to the base word, not cumulatively
    rules = ["l", "u", "$!", "^1", "d"]
    result = apply_hashcat_rules("hi", rules)
    assert "hi" in result  # rule: l (already lower)
    assert "HI" in result  # rule: u
    assert "hi!" in result  # rule: $!
    assert "1hi" in result  # rule: ^1
    assert "hihi" in result  # rule: d


def test_apply_rules_skip_comments():
    rules = ["# this is a comment", "l", ""]
    result = apply_hashcat_rules("HELLO", rules)
    assert "hello" in result
