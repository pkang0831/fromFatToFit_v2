#!/usr/bin/env python3
"""
Round 2 of featured snippets — same logic as apply_featured_snippets.py
but reads from featured_snippets_spec_round2.py instead.
"""

from __future__ import annotations
import sys
import importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

# Patch SPEC_FILE before importing apply_featured_snippets so the
# correct spec gets loaded.
import apply_featured_snippets as base  # type: ignore

base.SPEC_FILE = HERE / "featured_snippets_spec_round2.py"


def main() -> int:
    return base.main()


if __name__ == "__main__":
    sys.exit(main())
