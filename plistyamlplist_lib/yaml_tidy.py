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


# YAML 1.1 boolean tokens that look like ordinary strings. ruamel's default
# str representer emits these unquoted, which makes the next load coerce them
# to booleans. AutoPkg recipes use string values like DERIVE_MIN_OS: 'YES',
# so we explicitly quote any string that matches.
_YAML_11_BOOL_RE = re.compile(
    r"^(y|Y|yes|Yes|YES|n|N|no|No|NO"
    r"|true|True|TRUE|false|False|FALSE"
    r"|on|On|ON|off|Off|OFF)$"
)


def _build_yaml():
    """Build a round-trip YAML instance configured for AutoPkg recipes.

    Round-trip mode preserves comments, blank lines, quote styles, and
    block scalar styles across load/dump, which is essential for tidying
    real-world recipes without losing author intent.
    """
    yaml = YAML(typ="rt")
    yaml.width = float("inf")
    yaml.default_flow_style = False
    yaml.preserve_quotes = True
    yaml.indent(mapping=2, sequence=2, offset=0)

    def represent_str_bool_safe(representer, data):
        if _YAML_11_BOOL_RE.match(data):
            return representer.represent_scalar(
                "tag:yaml.org,2002:str", data, style="'"
            )
        return representer.represent_scalar("tag:yaml.org,2002:str", data)

    yaml.representer.add_representer(str, represent_str_bool_safe)
    return yaml


def tidy_yaml(in_path, out_path=""):
    """Tidy up yaml file."""
    if not in_path.endswith(".yaml"):
        print("Not processing {}\n".format(in_path))
        return

    try:
        in_file = open(in_path, "r")
    except IOError:
        print("ERROR: {} not found".format(in_path))
        return

    yaml = _build_yaml()

    try:
        input_data = yaml.load(in_file)
    except DuplicateKeyError:
        print("ERROR: Duplicate key found in {}\n".format(in_path))
        return
    finally:
        in_file.close()

    if input_data is None:
        return

    # handle conversion of AutoPkg recipes
    if in_path.endswith(".recipe.yaml"):
        handle_autopkg_recipes.optimise_autopkg_recipes(input_data)

    buf = io.StringIO()
    yaml.dump(input_data, buf)
    output = buf.getvalue()

    if in_path.endswith(".recipe.yaml"):
        output = handle_autopkg_recipes.format_autopkg_recipes(output)

    if not out_path:
        out_path = in_path
    try:
        out_file = open(out_path, "w")
    except IOError:
        print("ERROR: could not create {} ".format(out_path))
        return
    with out_file:
        out_file.write(output)
        print("Wrote to : {}\n".format(out_path))


def main():
    """Get the command line inputs if running this script directly."""
    if len(sys.argv) < 2:
        print("Usage: yaml_tidy.py <input-file> <output-file>")
        sys.exit(1)

    in_path = sys.argv[1]

    try:
        sys.argv[2]
    except Exception:
        out_path = in_path
    else:
        out_path = sys.argv[2]

    tidy_yaml(in_path, out_path)


if __name__ == "__main__":
    main()
