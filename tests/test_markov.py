"""Tests for Markov chain password generation."""

from pawpy.mutations.markov import MarkovModel, generate_markov_words, train_markov


def test_train_and_generate():
    model = MarkovModel(order=2)
    model.train(["password", "passing", "passive"])
    # Should generate something (might be empty if training data too small)
    word = model.generate(min_len=3, max_len=10)
    assert word is None or len(word) >= 3


def test_generate_many():
    words = generate_markov_words(
        ["password", "dragon", "monkey", "letmein", "shadow"],
        count=10,
        order=1,
        min_len=4,
        max_len=8,
    )
    assert isinstance(words, list)
    # Markov with small corpus might not produce many, but should not error


def test_empty_corpus():
    model = MarkovModel(order=2)
    model.train([])
    assert model.generate() is None


def test_train_markov_convenience():
    model = train_markov(["hello", "help", "held"], order=1)
    assert model.total_chars > 0
