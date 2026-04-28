#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""CLI entry point for tidying AutoPkg YAML recipes.

Accepts one or more file paths and tidies each in-place. Designed to be
invoked by tools (such as pre-commit) that pass a batch of file paths
as positional arguments.
"""

import sys

from .yaml_tidy import tidy_yaml


def main():
    if len(sys.argv) < 2:
        print("Usage: tidy-autopkg-recipes <file> [<file> ...]")
        sys.exit(1)

    rc = 0
    for path in sys.argv[1:]:
        try:
            tidy_yaml(path)
        except Exception as exc:  # pragma: no cover - surface and continue
            print("ERROR tidying {}: {}".format(path, exc), file=sys.stderr)
            rc = 1
    sys.exit(rc)


if __name__ == "__main__":
    main()
