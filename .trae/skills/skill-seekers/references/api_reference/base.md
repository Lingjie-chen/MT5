# API Reference: base.py

**Language**: Python

**Source**: `src\skill_seekers\cli\parsers\base.py`

---

## Classes

### SubcommandParser

Base class for subcommand parsers.

Each subcommand parser defines:
- name: Subcommand name (e.g., 'scrape')
- help: Short help text
- description: Long description (optional, defaults to help)
- add_arguments(): Method to add command-specific arguments

**Inherits from**: ABC

#### Methods

##### name(self) → str

Subcommand name (e.g., 'scrape', 'github', 'package').

**Decorators**: `@property`, `@abstractmethod`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |

**Returns**: `str`


##### help(self) → str

Short help text shown in command list.

**Decorators**: `@property`, `@abstractmethod`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |

**Returns**: `str`


##### description(self) → str

Long description (defaults to help text).

**Decorators**: `@property`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |

**Returns**: `str`


##### add_arguments(self, parser: argparse.ArgumentParser) → None

Add subcommand-specific arguments to parser.

Args:
    parser: ArgumentParser for this subcommand

**Decorators**: `@abstractmethod`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| parser | argparse.ArgumentParser | - | - |

**Returns**: `None`


##### create_parser(self, subparsers) → argparse.ArgumentParser

Create and configure subcommand parser.

Args:
    subparsers: Subparsers object from main parser

Returns:
    Configured ArgumentParser for this subcommand

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| subparsers | None | - | - |

**Returns**: `argparse.ArgumentParser`



