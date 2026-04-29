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

_SECTION_HEADERS = ("Input:", "Process:", "ParentRecipeTrustInfo:")


def optimise_autopkg_recipes(recipe):
    """Reorder an AutoPkg recipe in place to aid readability.

    Operates on a ruamel.yaml round-trip CommentedMap so that comments,
    blank lines, and quote/scalar styles are preserved.

    1. In each Process entry, move Comment and Arguments to the end so
       Processor stays first.
    2. Move NAME to the front of the Input mapping.
    3. Reorder top-level keys to the canonical order in _DESIRED_ORDER.
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

    Only operates on column-0 lines so that blank lines inside block
    scalars (script bodies, descriptions) are left untouched.
    """
    lines = output.split("\n")
    result = []
    for line in lines:
        is_section_header = (
            line and not line[0].isspace()
            and any(line.startswith(k) for k in _SECTION_HEADERS)
        )
        is_top_level_processor_item = line.startswith("- Processor:")

        if is_section_header or is_top_level_processor_item:
            # ensure exactly one blank line between this header and the
            # previous top-level content (none if this is the first line
            # or directly follows the parent key)
            while result and result[-1] == "":
                result.pop()
            if result:
                # don't add a blank line directly after "Process:" before
                # the very first "- Processor:" entry
                if is_top_level_processor_item and result[-1].rstrip() == "Process:":
                    pass
                else:
                    result.append("")
        result.append(line)

    return "\n".join(result)
