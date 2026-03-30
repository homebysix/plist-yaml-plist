# plist-yaml-plist Development Guide

## Overview

This tool converts between Apple plist, YAML, and JSON formats with special optimizations for AutoPkg recipes. The core functionality is split between a main CLI entry point (`plistyamlplist.py`) and modular conversion functions in `plistyamlplist_lib/`.

## Build and Test Commands

### Building
```bash
make
# Builds a macOS installer package at pkg/plistyamlplist/build/plistyamlplist-{version}.pkg
# Uses munkipkg and AutoPkg's Python environment
```

### Cleaning
```bash
make clean
# Removes build artifacts from pkg/plistyamlplist/payload and build directories
```

### Linting
```bash
pre-commit run --all-files
# Runs pre-commit hooks including:
# - Python AST validation
# - Trailing whitespace fixes
# - End-of-file fixers
# - Executable shebang checks
```

### Manual Testing
No automated test suite exists. Test manually with:
```bash
# Convert plist to yaml
./plistyamlplist.py test.plist

# Convert yaml to plist
./plistyamlplist.py test.yaml

# Tidy AutoPkg recipes
./plistyamlplist.py recipe.yaml --tidy
```

## Architecture

### Entry Point Flow
`plistyamlplist.py` determines conversion direction by:
1. Detecting file extension (.plist, .yaml, .json)
2. For plist files without extension: reads line 2 for "PLIST 1.0" declaration
3. Routing to appropriate converter in `plistyamlplist_lib/`

### Module Organization
- `plist_yaml.py` - Plist → YAML conversion
- `yaml_plist.py` - YAML → Plist conversion  
- `json_plist.py` - JSON → Plist conversion
- `yaml_tidy.py` - AutoPkg recipe reformatting (standalone or via `--tidy`)
- `handle_autopkg_recipes.py` - Recipe-specific optimizations
- `version.py` - Single source of truth for version string

### Special Path Handling
The tool recognizes `YAML`/`_YAML` and `JSON`/`_JSON` folders in paths:
- Input: `/path/to/YAML/subfolder/file.yaml`  
- Output (auto): `/path/to/subfolder/file.plist` (if `/path/to/subfolder` exists)

This convention allows maintaining parallel directory structures for source (YAML) and built (plist) files.

### Batch Conversion
- Glob patterns: `plistyamlplist '/path/to/*.yaml'` (escape the glob)
- Folder recursion: `plistyamlplist /path/to/YAML/` processes all subfolders
- Folder replication: `plistyamlplist /path/to/YAML/ /path/to/output/` mirrors structure

## Key Conventions

### AutoPkg Recipe Formatting
When converting AutoPkg recipes (identified by "Process" key), apply special formatting via `optimise_autopkg_recipes()`:

1. **Process array ordering**: Processor name first, then Comment, then Arguments
2. **Input dictionary**: NAME key always first
3. **Top-level keys**: Comment → Description → Identifier → ParentRecipe → MinimumVersion → Input → Process → ParentRecipeTrustInfo
4. **Blank lines**: Added before Input and Process sections, and between processor dictionaries (handled by YAML dumper config)

### YAML Library Configuration
Uses `ruamel.yaml` (version < 0.18.0 required):
- Preserves comments when round-tripping
- Custom representers for OrderedDict to maintain key order
- Auto-installs via pip if missing

### Version Management
- Version is single-sourced in `plistyamlplist_lib/version.py`
- `versionbump.py` updates `pkg/plistyamlplist/build-info.plist` from this version
- Run before building: the Makefile includes versionbump as a dependency

### Plist Detection
Don't rely solely on file extensions. The `check_if_plist()` function reads line 2 for the DOCTYPE declaration (`PLIST 1.0`) to handle extension-less files.

## Package Structure

Built packages install to:
- Binary: `/usr/local/bin/plistyamlplist`
- Library: `/usr/local/bin/plistyamlplist_lib/`

The main script imports from `plistyamlplist_lib` as a regular Python package, so both relative and absolute imports work depending on installation context.

## Dependencies

Runtime:
- Python 3.x (developed with 3.10+)
- `ruamel.yaml` < 0.18.0 (auto-installed if missing)
- macOS `plutil` command (for binary plist conversion)

Build:
- munkipkg (expected at `/usr/local/bin/munkipkg`)
- AutoPkg's Python environment (`/usr/local/autopkg/python`)

## Common Pitfalls

1. **Binary plists**: Must convert to XML first with `plutil -convert xml1` before conversion
2. **Glob escaping**: Shell expands globs before Python sees them—use `\*.yaml`
3. **Folder naming**: YAML/JSON folder detection is case-sensitive and requires exact matches
4. **Output path prompts**: If target folder doesn't exist, user must create it manually
5. **ruamel.yaml versions**: Version 0.18.0+ has breaking API changes—pin to < 0.18.0
