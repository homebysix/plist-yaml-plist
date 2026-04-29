#!/usr/bin/env python3
# -*- coding: utf-8 -*-


_DESIRED_ORDER = (
    "Comment",
    "Description",
    "Identifier",
    "ParentRecipe",
    "MinimumVersion",
    "Input",
    "Process",
    "ParentRecipeTrustInfo",
)

_TOP_LEVEL_TRIGGERS = (
    "Input:",
    "Process:",
    "ParentRecipeTrustInfo:",
    "- Processor:",
)


def optimise_autopkg_recipes(recipe):
    """Reorder an AutoPkg recipe in place to aid readability.

    Operates on a ruamel.yaml round-trip CommentedMap so that comments,
    blank lines, and quote/scalar styles are preserved.
    """
    process = recipe.get("Process")
    if process:
        for processor in process:
            if "Comment" in processor:
                processor.move_to_end("Comment")
            if "Arguments" in processor:
                processor.move_to_end("Arguments")

    input_block = recipe.get("Input")
    if input_block is not None and "NAME" in input_block:
        input_block.move_to_end("NAME", last=False)

    for key in _DESIRED_ORDER:
        if key in recipe:
            recipe.move_to_end(key)


def format_autopkg_recipes(output):
    """Ensure a single blank line precedes each top-level recipe section.

    Only operates on column-0 lines so blank lines inside block scalars
    (script bodies, descriptions) are left untouched.
    """
    result = []
    for line in output.split("\n"):
        is_trigger = line.startswith(_TOP_LEVEL_TRIGGERS)
        if not is_trigger:
            result.append(line)
            continue

        while result and result[-1] == "":
            result.pop()

        # don't add a blank line directly between "Process:" and its first item
        is_first_processor = (
            line.startswith("- Processor:")
            and result
            and result[-1].rstrip() == "Process:"
        )
        if result and not is_first_processor:
            result.append("")
        result.append(line)

    return "\n".join(result)
