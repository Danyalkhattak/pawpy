# Pawpy

**The Most Powerful Wordlist Generator**

<p align="center">
  <img src="https://img.shields.io/badge/version-1.0.0-blue" alt="Version" />
  <img src="https://img.shields.io/badge/python-3.8+-green" alt="Python" />
  <img src="https://img.shields.io/badge/license-MIT-orange" alt="License" />
  <img src="https://img.shields.io/badge/purpose-educational%20%7C%20authorised%20testing-red" alt="Purpose" />
</p>

---

## ⚠️ Ethical Use Only

Pawpy is designed **exclusively** for authorised security testing, password audits, and educational purposes. Unauthorised use against systems or accounts you do not own or have explicit permission to test is **illegal and unethical**. By using this tool, you confirm you have proper authorisation.

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [CLI Reference](#cli-reference)
- [Profile Format](#profile-format)
- [Mutation Engine](#mutation-engine)
- [Scoring & Filtering](#scoring--filtering)
- [API & Dashboard](#api--dashboard)
- [OSINT Plugins](#osint-plugins)
- [Project Structure](#project-structure)
- [Development](#development)
- [License](#license)

---

## Overview

Pawpy is an open-source, terminal-based wordlist generator a powerful mutation engine, Markov chain blending, hashcat rule-file support, hybrid mask attacks, and a built-in web dashboard. It transforms target profile information into comprehensive, policy-compliant password candidate lists suitable for authorised penetration testing and security research.

The tool follows a modular pipeline architecture: profile data flows through successive mutation stages (leet-speak, mangle rules, date permutations, keyboard walks, Markov blending, custom templates, hashcat rules, hybrid masks) before optional scoring and policy filtering produces the final deduplicated, sorted wordlist.

---

## Features

### Core

| Feature | Description |
|---------|-------------|
| **Interactive Profiling** | Questionnaire for collecting target information |
| **JSON Import** | Load single or multi-target profiles from JSON files |
| **Multi-Target Cross-Referencing** | Merge multiple profiles for cross-referenced word generation |
| **OSINT Plugin System** | Auto-discovery and execution of OSINT plugins from `profile/plugins/` |
| **Embedded Top 10K Passwords** | Ships with common passwords; auto-updatable from SecLists |

### Mutation Engine

| Mutation | Description |
|----------|-------------|
| **Leet Speak** | 3 substitution levels (basic, extended, aggressive) with combinatorial expansion |
| **Date Permutations** | 20+ variants per date: DDMM, MMDD, YYYY, YY, with separator combinations |
| **Common Mangle Rules** | Capitalise, upper, lower, reverse, swapcase, append/prepend digits & symbols |
| **Hashcat Rule Engine** | Full parser for hashcat/John-style `.rule` files (l, u, c, r, $X, ^X, sXY, iNX, oNX, d, p, z, [N, ]N) |
| **Static Keyboard Walks** | 25+ built-in classic patterns (qwerty, asdf, zxcvbn, 1qaz2wsx, ...) |
| **Dynamic Keyboard Walks** | BFS-generated walks on QWERTY adjacency graph up to configurable length |
| **Two-Word Combinations** | All pairs of base words with 8 separator variants and case combinations |
| **Year-Word Blends** | Append/prepend years (1990–current) and two-digit years to all base words |
| **Markov Blending** | Character-level Markov chain (order 1–4) trained on corpus + profile words |
| **Custom Templates** | Pattern engine: `[FirstName][Year][!]` with token resolution and combinatorial expansion |
| **Hybrid Mask Attacks** | Simulates hashcat `-a 6` (word + right mask) and `-a 7` (left mask + word) |

### Scoring & Filtering

| Feature | Description |
|---------|-------------|
| **zxcvbn Scoring** | Optional strength-based pruning (scores 0–4) to remove trivially weak candidates |
| **Policy Filtering** | Enforce minimum length, uppercase, lowercase, digit, and special character requirements |

### API & Dashboard

| Feature | Description |
|---------|-------------|
| **REST API** | FastAPI endpoint (`POST /generate`) accepting profile JSON, returning download URL |
| **Web Dashboard** | Browser-based UI with real-time WebSocket progress logging |

### Performance

| Feature | Description |
|---------|-------------|
| **Multi-Process** | Configurable worker count via `-t` / `--threads` |
| **GPU Acceleration** | Optional CuPy-based GPU rule application (graceful fallback to CPU) |
| **External Merge Sort** | Billion-scale sorting with k-way heap merge for very large wordlists |

### Modes

| Mode | Flag | Behaviour |
|------|------|----------|
| **Normal** | *(default)* | All standard mutations |
| **Lite** | `--lite` | Skips two-word combos, Markov, large hybrid, dynamic keyboard walks |
| **Extreme** | `--extreme` | Enables year blends, Markov, dynamic keyboard walks, all heavy mutations |

---

## Installation

### From PyPI (recommended)

```bash
pip install pawpy
```

### From Source

```bash
git clone https://github.com/Danyalkhattak/pawpy.git
cd pawpy
pip install -r requirements.txt
pip install -e .
```

### Optional Dependencies

```bash
# API & Dashboard
pip install fastapi uvicorn websockets

# GPU acceleration (requires CUDA)
pip install cupy-cuda11x   # or cupy-cuda12x depending on your CUDA version

# Password strength scoring
pip install zxcvbn

# All optional
pip install -e ".[all]"
```

---

## Quick Start

### Interactive Mode

```bash
pawpy
```

This launches the questionnaire. Answer the prompts (blank answers are fine) and Pawpy generates a wordlist to `pawpy_wordlist.txt`.

### From JSON Profile

```bash
pawpy -j profile.json -o wordlist.txt
```

### Multi-Target Mode

```bash
pawpy --multi targets.json --extreme
```

### With Hashcat Rules

```bash
pawpy -j profile.json --rules best64.rule
```

### Hybrid Mask Attack

```bash
pawpy -j profile.json --hybrid-right ?d?d?d
```

### With Scoring & Policy Filter

```bash
pawpy -j profile.json --min-strength 2 --min-length 8 --require-upper --require-digit
```

### Update Common Passwords

```bash
pawpy update-passwords
```

### Start API Server

```bash
pawpy api
# Server runs at http://127.0.0.1:8000
```

### Launch Dashboard

```bash
pawpy dashboard
# Dashboard runs at http://127.0.0.1:8080
```

---

## CLI Reference

```
usage: pawpy [-h] [-o FILE] [-j FILE] [--multi FILE] [--rules FILE]
               [--template TMPL] [--hybrid-left MASK] [--hybrid-right MASK]
               [--markov] [--markov-order N] [--markov-count N]
               [--min-strength N] [--min-length N]
               [--require-upper] [--require-lower] [--require-digit]
               [--require-special] [--lite] [--extreme]
               [--gpu] [-t N] [-v] [--verbose]

Options:
  -o, --output FILE         Output file (default: pawpy_wordlist.txt)
  -j, --import-json FILE    Import single profile from JSON
  --multi FILE              Import multiple profiles from JSON array
  --rules FILE              Load hashcat rule file
  --template TEMPLATE       Custom pattern template (repeatable)
  --hybrid-left MASK        Left mask for hybrid attack (?l?d)
  --hybrid-right MASK       Right mask for hybrid attack (?d?d?d)
  --markov                  Enable Markov chain blending
  --markov-order N          Markov chain order (default: 2)
  --markov-count N          Number of Markov words (default: 5000)
  --min-strength N          Minimum zxcvbn score (0-4)
  --min-length N            Minimum password length
  --require-upper           Require uppercase letter
  --require-lower           Require lowercase letter
  --require-digit           Require digit
  --require-special         Require special character
  --lite                    Fast mode (skip heavy combos)
  --extreme                 Enable all heavy mutations
  --gpu                     Use GPU acceleration if available
  -t, --threads N           Worker process count (default: CPU count)
  -v, --version             Show version
  --verbose                 Enable debug logging

Sub-commands:
  update-passwords          Download latest common passwords from SecLists
  api                       Start REST API server
  dashboard                 Launch web dashboard
```

---

## Profile Format

### Single Profile (JSON)

```json
{
  "firstname": "John",
  "lastname": "Doe",
  "nickname": "Johnny",
  "birthdate": "01011990",
  "partner": "Jane",
  "partner_nick": "Janey",
  "partner_bdate": "02021992",
  "pet": "Rex",
  "company": "Acme",
  "hometown": "Metropolis",
  "favourite_color": "blue",
  "children": ["Alice", "Bob"],
  "keywords": ["guitar", "hiking"]
}
```

### Multi-Target Profile (JSON Array)

```json
[
  { "firstname": "John", "lastname": "Doe", "pet": "Rex" },
  { "firstname": "Jane", "lastname": "Doe", "pet": "Buddy" }
]
```

When using `--multi`, Pawpy merges all profiles into a unified cross-referenced profile. This means base words from all targets are combined, enabling the mutation engine to generate cross-target combinations (e.g., John's first name paired with Jane's pet name).

---

## Mutation Engine

The mutation pipeline processes base words through multiple stages in sequence:

```
Base Words
    │
    ├── Leet Speak (3 levels)
    ├── Common Mangle Rules (capitalize, reverse, append/prepend)
    ├── Date Permutations (20+ variants per date)
    ├── Hashcat Rules (if --rules provided)
    ├── Custom Templates (if --template provided)
    ├── Keyboard Walks (static + optional dynamic)
    ├── Markov Blending (if --markov)
    ├── Year-Word Blends (if not --lite)
    ├── Two-Word Combinations (if not --lite)
    ├── Hybrid Masks (if --hybrid-left/right)
    └── Top 10K Common Passwords
    │
    ▼
Scoring & Policy Filtering
    │
    ▼
Deduplication & Sort → Final Wordlist
```

### Leet Speak Levels

| Level | Substitutions |
|-------|---------------|
| 1 (Basic) | a→@, e→3, i→1, o→0, s→$, t→7 |
| 2 (Extended) | + i→!, s→5 |
| 3 (Aggressive) | + a→4, l→1, b→8, g→9, h→# |

### Hashcat Rule Support

Supported rule commands:

| Rule | Description | Example |
|------|-------------|--------|
| `l` | Lowercase all | `hello` → `hello` |
| `u` | Uppercase all | `hello` → `HELLO` |
| `c` | Capitalise first | `hello` → `Hello` |
| `s` | Swap case | `Hello` → `hELLO` |
| `r` | Reverse | `hello` → `olleh` |
| `d` | Duplicate whole word | `hi` → `hihi` |
| `p` | Duplicate first char | `hi` → `hhi` |
| `z` | Duplicate last char | `hi` → `hii` |
| `$X` | Append char X | `$!` → `pass!` |
| `^X` | Prepend char X | `^1` → `1pass` |
| `[N` | Keep first N chars | `[3` → `pas` |
| `]N` | Keep last N chars | `]3` → `ssw` |
| `iNX` | Insert char X at pos N | `i2X` → `paXssword` |
| `oNX` | Overwrite char at pos N with X | `o0X` → `Xassword` |
| `'XY` | Replace all X with Y | `'a@` → `p@ssword` |

### Template Tokens

| Token | Resolves To |
|-------|-------------|
| `[FirstName]` | First name (original, Capitalised, UPPER, lower) |
| `[LastName]` | Last name |
| `[Nickname]` | Nickname |
| `[Pet]` | Pet name |
| `[Company]` | Company name |
| `[Color]` / `[Favourite_Color]` | Favourite colour |
| `[Partner]` | Partner's first name |
| `[Child]` / `[Children]` | Children's names |
| `[Keyword]` / `[Keywords]` | Keywords / interests |
| `[Year]` | 1986–current year |
| `[Year2]` | Two-digit years |
| `[Date]` | Birthdate from profile |
| `[Digit]` | 0–9 |
| `[Special]` | !@#$%^&*?._- |
| `[Upper]` | A–Z |
| `[Lower]` | a–z |
| `[Sep]` | Separators: _ - . @ # (empty) |
| `[123]` | 123, 1234, 12345, !@#, 1q2w3e |

Example: `[FirstName][Sep][Year]` with profile `firstname=John` generates:
`john_2024`, `john-2024`, `john.2024`, `John_2024`, `john@2024`, etc.

---

## Scoring & Filtering

### zxcvbn Strength Scoring

When `--min-strength N` is provided (requires `zxcvbn` package), each candidate is scored on a 0–4 scale:

| Score | Strength | Description |
|-------|----------|-------------|
| 0 | Very Weak | Trivially guessable (e.g., `123456`) |
| 1 | Weak | Easily guessable (e.g., `password1`) |
| 2 | Fair | Moderately guessable |
| 3 | Strong | Uncommon but not resistant to targeted attacks |
| 4 | Very Strong | Highly resistant to cracking |

Candidates scoring below the threshold are pruned. This reduces wordlist size by removing trivially weak entries while keeping genuinely strong candidates.

### Policy Filtering

Combine policy flags to enforce password complexity requirements:

```bash
# At least 8 chars, one uppercase, one digit
pawpy -j profile.json --min-length 8 --require-upper --require-digit

# Complex: 10+ chars, mixed case, digit, special
pawpy -j profile.json --min-length 10 --require-upper --require-lower \
    --require-digit --require-special
```

---

## API & Dashboard

### REST API

Start the API server:

```bash
pawpy api
```

Endpoints:

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | Health check |
| POST | `/generate` | Generate wordlist (multipart: profile JSON file + options) |
| GET | `/download/{job_id}` | Download generated wordlist |
| GET | `/jobs` | List all generation jobs |

Example with `curl`:

```bash
curl -X POST http://127.0.0.1:8000/generate \
  -F "profile=@target.json" \
  -F "output=my_wordlist.txt" \
  -F "extreme=true"
```

### Web Dashboard

```bash
pawpy dashboard
# Open http://127.0.0.1:8080 in your browser
```

The dashboard provides a dark-themed web interface where you can:

- Upload a profile JSON file
- Select generation mode (Normal / Lite / Extreme)
- Toggle Markov blending and zxcvbn scoring
- Monitor real-time generation progress via WebSocket
- Download the resulting wordlist

---

## OSINT Plugins

Pawpy includes a plugin system that auto-discovers Python modules in `pawpy/profile/plugins/`. Each plugin must define a `collect(profile: dict) -> dict` function that enriches the profile dict with OSINT-derived data.

### Creating a Plugin

Create a new `.py` file in `pawpy/profile/plugins/`:

```python
# pawpy/profile/plugins/my_plugin.py

from typing import Any, Dict


def collect(profile: Dict[str, Any]) -> Dict[str, Any]:
    """Enrich profile with OSINT data."""
    # Your OSINT logic here
    # e.g., look up public social media profiles,
    # check for breached credentials (with consent), etc.
    
    if profile.get("firstname"):
        keywords = profile.get("keywords", [])
        if isinstance(keywords, str):
            keywords = [keywords]
        # Add OSINT-discovered keywords
        keywords.append("discovered_keyword")
        profile["keywords"] = keywords
    
    return profile
```

### Important Rules for Plugin Authors

- **Respect rate-limiting** and terms of service of any external APIs or websites.
- **Only use OSINT data for authorised security testing.**
- **Follow responsible disclosure** practices.
- Handle exceptions gracefully so plugin failures don't crash the pipeline.

---

## Project Structure

```
pawpy/
├── pawpy/
│   ├── __init__.py              # Package version and metadata
│   ├── __main__.py              # python -m pawpy entry point
│   ├── cli.py                   # Full CLI with argparse
│   ├── config.py                # PawpyConfig dataclass
│   ├── utils.py                 # Banner, logging, dedup, progress
│   ├── profile/
│   │   ├── __init__.py
│   │   ├── base.py              # ProfileCollector (interactive + JSON)
│   │   ├── multi.py             # Multi-target cross-referencing
│   │   └── plugins/
│   │       ├── __init__.py      # Plugin discovery and loader
│   │       └── example.py       # Example no-op plugin template
│   ├── mutations/
│   │   ├── __init__.py
│   │   ├── leet.py              # Leet-speak (3 levels, combinatorial)
│   │   ├── dates.py             # Date permutations (20+ variants)
│   │   ├── mangle.py            # Common rules + hashcat rule engine
│   │   ├── markov.py            # Markov chain training & generation
│   │   ├── keyboard.py          # Static + dynamic keyboard walks
│   │   └── templates.py         # Custom pattern template engine
│   ├── generator/
│   │   ├── __init__.py
│   │   ├── core.py              # Main 15-stage pipeline orchestrator
│   │   ├── hybrid.py            # Hybrid mask attacks (hashcat -a 6/7)
│   │   ├── sorter.py            # Billion-scale external merge sort
│   │   └── gpu.py               # Optional CuPy GPU acceleration
│   ├── scoring/
│   │   ├── __init__.py
│   │   └── scorer.py            # zxcvbn-based strength pruning
│   ├── filters/
│   │   ├── __init__.py
│   │   └── policy.py            # Password complexity policy filter
│   ├── api/
│   │   ├── __init__.py
│   │   ├── rest.py              # FastAPI REST endpoints
│   │   └── dashboard.py         # WebSocket web dashboard
│   └── data/
│       ├── __init__.py
│       ├── common_passwords.py  # Embedded top 100 + SecLists loader
│       └── updater.py           # Auto-update from SecLists
├── tests/
│   ├── __init__.py
│   ├── test_leet.py
│   ├── test_dates.py
│   ├── test_mangle.py
│   ├── test_markov.py
│   ├── test_keyboard.py
│   ├── test_templates.py
│   ├── test_profile.py
│   ├── test_hybrid.py
│   └── test_policy.py
├── .github/
│   └── workflows/
│       └── lint.yml             # CI: flake8 + black + isort
├── requirements.txt
├── setup.py
└── README.md
```

---

## Development

### Setup

```bash
git clone https://github.com/Danyalkhattak/pawpy.git
cd pawpy
pip install -e ".[all]"
pip install pytest
```

### Running Tests

```bash
pytest tests/ -v
```

### Code Quality

```bash
# Lint
flake8 pawpy/

# Format
black pawpy/
isort pawpy/

# All checks (also run by CI)
flake8 pawpy/ && black --check pawpy/ && isort --check-only pawpy/
```

### Adding a New Mutation

Create a new `.py` file in `pawpy/mutations/` with a function that takes a list of words and returns a list of mutated candidates:

```python
# pawpy/mutations/my_mutation.py

def my_mutation(word: str) -> list[str]:
    """Apply custom mutation to a word."""
 return [word + "_custom", word.upper() + "123"]
```

Then import and call it in `pawpy/generator/core.py` within the `PipelineOrchestrator.run()` method.

---

## Architecture & Data Flow

```
User Input (CLI / JSON / API)
         │
         ▼
┌─────────────────────┐
│  Profile Collection  │  Interactive / JSON / OSINT Plugins
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Base Word Extract   │  All text fields → lowercase, deduplicated
│  + Date Extraction   │
└──────────┬──────────┘
           │
           ▼
┌──────────────────────────────────────────┐
│           Mutation Pipeline               │
│  ┌──────────┐ ┌──────────┐ ┌───────────┐  │
│  │  Leet    │ │  Mangle  │ │  Dates    │  │
│  └──────────┘ └──────────┘ └───────────┘  │
│  ┌──────────┐ ┌──────────┐ ┌───────────┐  │
│  │ Keyboard │ │  Markov  │ │ Templates │  │
│  └──────────┘ └──────────┘ └───────────┘  │
│  ┌──────────┐ ┌──────────┐ ┌───────────┐  │
│  │  Hybrid  │ │  Rules   │ │  Combos   │  │
│  └──────────┘ └──────────┘ └───────────┘  │
└────────────────────┬─────────────────────┘
                     │
                     ▼
┌──────────────────────────────────────────┐
│         Scoring & Filtering              │
│  zxcvbn strength  │  Policy compliance   │
└────────────────────┬─────────────────────┘
                     │
                     ▼
┌──────────────────────────────────────────┐
│         Sort + Deduplicate                │
│  (in-memory or external merge sort)      │
└────────────────────┬─────────────────────┘
                     │
                     ▼
              Final Wordlist File
```

---

## Performance Notes

- **Throughput**: On an 8-core CPU, the system targets ≥10 million passwords/minute for basic mutations.
- **Memory**: By default, stays under 2 GB RAM. For very large generation jobs, the external merge sorter handles disk-backed processing.
- **Output**: Written sequentially for optimal I/O. Sorted chunks are merge-sorted efficiently.
- **GPU**: Optional CuPy acceleration for rule application. Falls back gracefully to CPU if CuPy is not installed.

---

## License

MIT License. See [LICENSE](LICENSE) for details.

---

## Acknowledgements

- [CUPP](https://github.com/Mebus/cupp) – Original inspiration for interactive profiling
- [Hashcat](https://hashcat.net/wiki/doku.php?id=rule_based_attack) – Rule engine format
- [SecLists](https://github.com/danielmiessler/SecLists) – Common password data source
- [zxcvbn](https://github.com/dropbox/zxcvbn) – Password strength estimation
- [Rich](https://github.com/Textualize/rich) – Beautiful terminal output
