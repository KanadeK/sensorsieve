from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

from sensorsieve import __version__
from sensorsieve.compare import compare_results
from sensorsieve.detect import analyze_session
from sensorsieve.errors import SensorSieveError
from sensorsieve.images import load_session
from sensorsieve.report import assert_output_available, write_comparison, write_inspection


def _sensitivity(value: str) -> float:
    parsed = float(value)
    if not 2.0 <= parsed <= 12.0:
        raise argparse.ArgumentTypeError("must be between 2.0 and 12.0")
    return parsed


def _max_side(value: str) -> int:
    parsed = int(value)
    if not 512 <= parsed <= 8192:
        raise argparse.ArgumentTypeError("must be between 512 and 8192")
    return parsed


def _add_analysis_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--sensitivity", default=4.0, type=_sensitivity)
    parser.add_argument("--max-side", default=2048, type=_max_side)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="sensorsieve",
        description="Offline multi-frame camera sensor dust evidence.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    commands = parser.add_subparsers(dest="command", required=True)
    inspect_parser = commands.add_parser(
        "inspect", help="analyze one multi-frame flat-field session"
    )
    inspect_parser.add_argument("input_dir", type=Path)
    _add_analysis_arguments(inspect_parser)
    compare_parser = commands.add_parser(
        "compare", help="compare flat-field sessions from before and after cleaning"
    )
    compare_parser.add_argument("before_dir", type=Path)
    compare_parser.add_argument("after_dir", type=Path)
    _add_analysis_arguments(compare_parser)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "inspect":
            output_dir: Path = args.output
            assert_output_available(output_dir)
            session = load_session(args.input_dir, max_side=args.max_side)
            result = analyze_session(session, sensitivity=args.sensitivity)
            write_inspection(result, output_dir)
            if result.spots:
                noun = "spot" if len(result.spots) == 1 else "spots"
                print(f"review: {len(result.spots)} persistent {noun}; artifacts written")
                return 1
            print("clean: no persistent spots; artifacts written")
            return 0
        if args.command == "compare":
            output_dir = args.output
            assert_output_available(output_dir)
            before = analyze_session(
                load_session(args.before_dir, max_side=args.max_side),
                sensitivity=args.sensitivity,
            )
            after = analyze_session(
                load_session(args.after_dir, max_side=args.max_side),
                sensitivity=args.sensitivity,
            )
            comparison = compare_results(before, after)
            write_comparison(comparison, output_dir)
            counts = (
                f"{len(comparison.persistent)} persistent, "
                f"{len(comparison.new)} new, {len(comparison.resolved)} resolved"
            )
            if comparison.persistent or comparison.new:
                print(f"review: {counts}; artifacts written")
                return 1
            print(f"clean: {counts}; artifacts written")
            return 0
    except SensorSieveError as error:
        print(f"sensorsieve: error: {error}", file=sys.stderr)
        return 2
    raise AssertionError("argparse accepted an unknown command")
