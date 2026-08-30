from __future__ import annotations

import argparse
from collections.abc import Sequence

from sensorsieve import __version__


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="sensorsieve",
        description="Offline multi-frame camera sensor dust evidence.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    build_parser().parse_args(argv)
    return 0
