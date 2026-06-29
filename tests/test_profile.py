"""Tests for profile collection."""

from pawpy.profile.base import ProfileCollector
from pawpy.profile.multi import extract_merged_base_words, merge_profiles


def test_extract_base_words():
    profile = {
        "firstname": "John",
        "lastname": "Doe",
        "pet": "Rex",
        "children": ["Alice", "Bob"],
        "keywords": ["guitar", "hiking"],
        "birthdate": "01011990",
    }
    words = ProfileCollector.extract_base_words(profile)
    assert "john" in words
    assert "doe" in words
    assert "rex" in words
    assert "alice" in words
    assert "bob" in words
    assert "guitar" in words


def test_extract_dates():
    profile = {"birthdate": "01011990", "partner_bdate": "15051992"}
    dates = ProfileCollector.extract_dates(profile)
    assert "01011990" in dates
    assert "15051992" in dates


def test_merge_profiles():
    profiles = [
        {"firstname": "John", "pet": "Rex", "birthdate": "01011990"},
        {"firstname": "Jane", "pet": "Buddy", "birthdate": "15051992"},
    ]
    merged = merge_profiles(profiles)
    assert "John" in merged["firstname"]
    assert "Jane" in merged["firstname"]
    assert "Rex" in merged["pet"]
    assert "Buddy" in merged["pet"]


def test_extract_merged_words():
    profiles = [
        {"firstname": "John", "pet": "Rex"},
        {"firstname": "Jane", "pet": "Buddy", "company": "Acme"},
    ]
    merged = merge_profiles(profiles)
    words = extract_merged_base_words(merged)
    assert "john" in words
    assert "jane" in words
    assert "rex" in words
    assert "acme" in words
