# API Reference: main.py

**Language**: Python

**Source**: `src\skill_seekers\cli\main.py`

---

## Functions

### create_parser() → argparse.ArgumentParser

Create the main argument parser with subcommands.

**Returns**: `argparse.ArgumentParser`



### _reconstruct_argv(command: str, args: argparse.Namespace) → list[str]

Reconstruct sys.argv from args namespace for command module.

Args:
    command: Command name
    args: Parsed arguments namespace

Returns:
    List of command-line arguments for the command module

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| command | str | - | - |
| args | argparse.Namespace | - | - |

**Returns**: `list[str]`



### main(argv: list[str] | None = None) → int

Main entry point for the unified CLI.

Args:
    argv: Command-line arguments (defaults to sys.argv)

Returns:
    Exit code (0 for success, non-zero for error)

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| argv | list[str] | None | None | - |

**Returns**: `int`



### _handle_analyze_command(args: argparse.Namespace) → int

Handle analyze command with special post-processing logic.

Args:
    args: Parsed arguments

Returns:
    Exit code

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| args | argparse.Namespace | - | - |

**Returns**: `int`


