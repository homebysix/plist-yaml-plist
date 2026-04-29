#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""If this script is run directly, it takes an input file
from the command line. The input file must be in YAML format. The output file
will be in YAML format:

yaml_tidy.py <input-file>

The output file can be omitted. In this case, the input file will be overwritten.
"""

import io
import re
import subprocess
import sys

try:
    from ruamel.yaml import YAML
    from ruamel.yaml.constructor import DuplicateKeyError
except ImportError:
    subprocess.check_call([sys.executable, "-m", "ensurepip", "--user"])
    subprocess.check_call(
        [
            sys.executable,
            "-m",
            "pip",
            "install",
            "-U",
            "pip",
            "setuptools",
            "wheel",
            "ruamel.yaml<0.18.0",
            "--user",
        ]
    )
    from ruamel.yaml import YAML
    from ruamel.yaml.constructor import DuplicateKeyError

from . import handle_autopkg_recipes


# YAML 1.1 boolean tokens that look like ordinary strings. ruamel emits these
# unquoted by default, so the next load coerces them to booleans. AutoPkg
# recipes use string values like DERIVE_MIN_OS: 'YES'.
_YAML_11_BOOL_RE = re.compile(
    r"^(y|Y|yes|Yes|YES|n|N|no|No|NO"
    r"|true|True|TRUE|false|False|FALSE"
    r"|on|On|ON|off|Off|OFF)$"
)


def _represent_str_bool_safe(representer, data):
    if _YAML_11_BOOL_RE.match(data):
        return representer.represent_scalar("tag:yaml.org,2002:str", data, style="'")
    return representer.represent_scalar("tag:yaml.org,2002:str", data)


def build_yaml():
    """Build a round-trip YAML instance configured for AutoPkg recipes.

    Round-trip mode preserves comments, blank lines, quote styles, and
    block scalar styles across load/dump.
    """
    yaml = YAML(typ="rt")
    yaml.width = float("inf")
    yaml.default_flow_style = False
    yaml.preserve_quotes = True
    yaml.indent(mapping=2, sequence=2, offset=0)
    yaml.representer.add_representer(str, _represent_str_bool_safe)
    return yaml


def tidy_yaml(in_path, out_path="", yaml=None):
    """Tidy up yaml file. ``yaml`` may be a pre-built ruamel.yaml YAML
    instance to avoid per-call construction in batch use."""
    if not in_path.endswith(".yaml"):
        print("Not processing {}\n".format(in_path))
        return

    if yaml is None:
        yaml = build_yaml()

    is_recipe = in_path.endswith(".recipe.yaml")

    try:
        with open(in_path, "r") as in_file:
            input_data = yaml.load(in_file)
    except IOError:
        print("ERROR: {} not found".format(in_path))
        return
    except DuplicateKeyError:
        print("ERROR: Duplicate key found in {}\n".format(in_path))
        return

    if input_data is None:
        return

    if is_recipe:
        handle_autopkg_recipes.optimise_autopkg_recipes(input_data)

    if not out_path:
        out_path = in_path

    try:
        out_file = open(out_path, "w")
    except IOError:
        print("ERROR: could not create {} ".format(out_path))
        return

    with out_file:
        if is_recipe:
            buf = io.StringIO()
            yaml.dump(input_data, buf)
            out_file.write(handle_autopkg_recipes.format_autopkg_recipes(buf.getvalue()))
        else:
            yaml.dump(input_data, out_file)
        print("Wrote to : {}\n".format(out_path))


def main():
    """Get the command line inputs if running this script directly."""
    if len(sys.argv) < 2:
        print("Usage: yaml_tidy.py <input-file> <output-file>")
        sys.exit(1)

    in_path = sys.argv[1]
    out_path = sys.argv[2] if len(sys.argv) > 2 else in_path
    tidy_yaml(in_path, out_path)


if __name__ == "__main__":
    main()
