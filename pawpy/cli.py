"""Pawpy command-line interface.

Parses all CLI options, displays the banner, orchestrates profile collection
and the generation pipeline, and handles sub-commands (update-passwords,
api, dashboard).
"""

from __future__ import annotations

import argparse
import logging
import sys
import asyncio
from pawpy import __version__
from pawpy.config import PawpyConfig
from pawpy.utils import confirm_ethical_use, console, print_banner, setup_logging

logger = logging.getLogger("pawpy")


def build_parser() -> argparse.ArgumentParser:
    """Build and return the argument parser with all options."""
    parser = argparse.ArgumentParser(
        prog="pawpy",
        description="Pawpy – The Most Powerful Educational Wordlist Generator",
        epilog=(
            "Examples:\n"
            "  pawpy                                    # Interactive mode\n"
            "  pawpy -j profile.json -o wordlist.txt   # From JSON profile\n"
            "  pawpy --multi targets.json --extreme      # Multi-target extreme mode\n"
            "  pawpy --rules best64.rule --markov       # Rules + Markov blending\n"
            "  pawpy --hybrid-left ?l?d -o hybrid.txt   # Hybrid mask attack\n"
            "  pawpy --min-length 8 --require-upper     # Policy-filtered output\n"
            "  pawpy update-passwords                   # Download latest SecLists\n"
            "  pawpy api                                # Start REST API\n"
            "  pawpy dashboard                          # Launch web dashboard\n"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    # --- I/O ---
    parser.add_argument(
        "-o",
        "--output",
        default="pawpy_wordlist.txt",
        help="Output file path (default: pawpy_wordlist.txt)",
    )
    parser.add_argument(
        "-j",
        "--import-json",
        dest="profile_json",
        help="Import a single target profile from a JSON file",
    )
    parser.add_argument(
        "--multi",
        help="Import multiple profiles from a JSON array file",
    )
    parser.add_argument(
        "--rules",
        help="Load a hashcat/John-style .rule file",
    )
    parser.add_argument(
        "--template",
        action="append",
        default=[],
        dest="templates",
        help="Custom pattern template, e.g. [FirstName][Year][!] (repeatable)",
    )

    # --- Hybrid masks ---
    parser.add_argument(
        "--hybrid-left",
        help="Left mask for hybrid attack (hashcat -a 7), e.g. ?l?d",
    )
    parser.add_argument(
        "--hybrid-right",
        help="Right mask for hybrid attack (hashcat -a 6), e.g. ?d?d?d",
    )

    # --- Markov ---
    parser.add_argument(
        "--markov",
        action="store_true",
        help="Enable Markov chain blending",
    )
    parser.add_argument(
        "--markov-order",
        type=int,
        default=2,
        help="Markov chain order (default: 2)",
    )
    parser.add_argument(
        "--markov-count",
        type=int,
        default=5000,
        help="Number of Markov-generated words (default: 5000)",
    )

    # --- Scoring / filtering ---
    parser.add_argument(
        "--min-strength",
        type=int,
        choices=[0, 1, 2, 3, 4],
        help="Minimum zxcvbn strength score (0-4). Requires zxcvbn installed.",
    )
    parser.add_argument(
        "--min-length",
        type=int,
        help="Minimum password length",
    )
    parser.add_argument(
        "--require-upper",
        action="store_true",
        help="Policy: require at least one uppercase letter",
    )
    parser.add_argument(
        "--require-lower",
        action="store_true",
        help="Policy: require at least one lowercase letter",
    )
    parser.add_argument(
        "--require-digit",
        action="store_true",
        help="Policy: require at least one digit",
    )
    parser.add_argument(
        "--require-special",
        action="store_true",
        help="Policy: require at least one special character",
    )

    # --- Modes ---
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument(
        "--lite",
        action="store_true",
        help="Fast mode: skip heavy combinations (two-word, Markov, large hybrid)",
    )
    mode_group.add_argument(
        "--extreme",
        action="store_true",
        help="Enable all heavy mutations (year blends, Markov, dynamic keyboard walks)",
    )

    # --- Performance ---
    parser.add_argument(
        "--gpu",
        action="store_true",
        help="Use GPU acceleration if CuPy is available",
    )
    parser.add_argument(
        "-t",
        "--threads",
        type=int,
        default=None,
        help="Number of worker processes (default: CPU count)",
    )

    # --- Meta ---
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose (debug) logging",
    )

    return parser


def build_config(args: argparse.Namespace) -> PawpyConfig:
    """Convert parsed arguments into a PawpyConfig object."""
    import multiprocessing

    config = PawpyConfig(
        output_file=args.output,
        profile_json=args.profile_json,
        multi_json=args.multi,
        rule_file=args.rules,
        templates=args.templates,
        hybrid_left=args.hybrid_left,
        hybrid_right=args.hybrid_right,
        markov=args.markov,
        markov_order=args.markov_order,
        markov_count=args.markov_count,
        min_strength=args.min_strength,
        min_length=args.min_length,
        require_upper=args.require_upper,
        require_lower=args.require_lower,
        require_digit=args.require_digit,
        require_special=args.require_special,
        lite=args.lite,
        extreme=args.extreme,
        gpu=args.gpu,
        threads=args.threads if args.threads else multiprocessing.cpu_count() or 4,
    )
    return config


def handle_update_passwords() -> None:
    """Handle the 'update-passwords' sub-command."""
    from pawpy.data.updater import update_common_passwords

    console.print("[cyan]Downloading latest common passwords from SecLists...[/cyan]")
    try:
        path = update_common_passwords()
        console.print(f"[green]Updated common passwords saved to:[/green] {path}")
    except Exception as e:
        console.print(f"[red]Failed to update:[/red] {e}")
        sys.exit(1)


def handle_api() -> None:
    """Handle the 'api' sub-command."""
    from pawpy.api.rest import run_api

    console.print("[cyan]Starting Pawpy REST API...[/cyan]")
    try:
        run_api()
    except ImportError as e:
        console.print(f"[red]Missing dependency:[/red] {e}")
        sys.exit(1)


def handle_dashboard() -> None:
    """Handle the 'dashboard' sub-command."""
    from pawpy.api.dashboard import run_dashboard

    console.print("[cyan]Starting Pawpy Web Dashboard...[/cyan]")
    try:
        asyncio.run(run_dashboard())
    except ImportError as e:
        console.print(f"[red]Missing dependency:[/red] {e}")
        sys.exit(1)


def main(argv: list = None) -> None:
    """Main entry point for the Pawpy CLI."""
    # Handle sub-commands first (they don't need the full parser)
    if argv is None:
        argv = sys.argv[1:]

    if not argv:
        # No args → show banner, then interactive mode
        pass
    elif argv[0] == "update-passwords":
        handle_update_passwords()
        return
    elif argv[0] == "api":
        handle_api()
        return
    elif argv[0] == "dashboard":
        handle_dashboard()
        return

    # Parse arguments
    parser = build_parser()
    args = parser.parse_args(argv)

    setup_logging()

    # Print banner and ethical warning
    print_banner()

    # For interactive mode, confirm ethical use
    if not args.profile_json and not args.multi:
        if not confirm_ethical_use():
            console.print("[yellow]Authorisation not confirmed. Exiting.[/yellow]")
            sys.exit(0)
    else:
        console.print(
            "[dim]Note: Ensure you have explicit authorisation to test "
            "target accounts.[/dim]\n"
        )

    # Build configuration
    config = build_config(args)

    # Collect profile
    from pawpy.generator.core import PipelineOrchestrator
    from pawpy.profile.base import ProfileCollector
    from pawpy.profile.multi import (
        extract_merged_base_words,
        load_multi_profiles,
        merge_profiles,
    )

    if config.multi_json:
        console.print(
            f"[cyan]Loading multi-target profiles from:[/cyan] {config.multi_json}"
        )
        profiles = load_multi_profiles(config.multi_json)
        merged = merge_profiles(profiles)
        profile = merged
        base_words = extract_merged_base_words(merged)
        console.print(
            f"[green]Extracted {len(base_words)} unique base words from {len(profiles)} profiles.[/green]\n"
        )
    else:
        collector = ProfileCollector()
        profile = collector.run(config)
        base_words = ProfileCollector.extract_base_words(profile)
        if base_words:
            console.print(
                f"[green]Extracted {len(base_words)} base words from profile.[/green]\n"
            )

    # GPU availability check
    if config.gpu:
        from pawpy.generator.gpu import is_gpu_available

        if is_gpu_available():
            console.print("[green]GPU acceleration enabled (CuPy detected).[/green]\n")
        else:
            console.print(
                "[yellow]CuPy not installed. GPU mode requested but falling back to CPU.[/yellow]\n"
            )
            console.print(
                "[dim]Install CuPy for GPU support: pip install cupy-cuda11x (or cupy-cuda12x)[/dim]\n"
            )

    # Run the generation pipeline
    try:
        orchestrator = PipelineOrchestrator(config, profile)
        output_path = orchestrator.run()
        console.print(f"\n[bold green]Wordlist saved to: {output_path}[/bold green]")
    except KeyboardInterrupt:
        console.print("\n[yellow]Generation interrupted by user.[/yellow]")
        sys.exit(130)
    except Exception as e:
        logger.exception("Generation failed")
        console.print(f"\n[bold red]Error:[/bold red] {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
