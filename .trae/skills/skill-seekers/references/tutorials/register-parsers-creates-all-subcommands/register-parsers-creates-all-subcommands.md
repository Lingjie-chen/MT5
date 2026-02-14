# How To: Register Parsers Creates All Subcommands

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: Test that register_parsers creates all 19 subcommands.

## Prerequisites

**Required Modules:**
- `argparse`
- `pytest`
- `skill_seekers.cli.parsers`
- `skill_seekers.cli.parsers.scrape_parser`
- `skill_seekers.cli.parsers.github_parser`
- `skill_seekers.cli.parsers.package_parser`
- `skill_seekers.cli.parsers.analyze_parser`


## Step-by-Step Guide

### Step 1: 'Test that register_parsers creates all 19 subcommands.'

```python
'Test that register_parsers creates all 19 subcommands.'
```

**Verification:**
```python
assert args.command is not None
```

### Step 2: Assign main_parser = argparse.ArgumentParser(...)

```python
main_parser = argparse.ArgumentParser()
```

### Step 3: Assign subparsers = main_parser.add_subparsers(...)

```python
subparsers = main_parser.add_subparsers(dest='command')
```

### Step 4: Call register_parsers()

```python
register_parsers(subparsers)
```

### Step 5: Assign test_commands = value

```python
test_commands = ['config --show', 'scrape --config test.json', 'github --repo owner/repo', 'package output/test/', 'upload test.zip', 'analyze --directory .', 'enhance output/test/', 'estimate test.json']
```

### Step 6: Assign args = main_parser.parse_args(...)

```python
args = main_parser.parse_args(cmd.split())
```

**Verification:**
```python
assert args.command is not None
```


## Complete Example

```python
# Workflow
'Test that register_parsers creates all 19 subcommands.'
main_parser = argparse.ArgumentParser()
subparsers = main_parser.add_subparsers(dest='command')
register_parsers(subparsers)
test_commands = ['config --show', 'scrape --config test.json', 'github --repo owner/repo', 'package output/test/', 'upload test.zip', 'analyze --directory .', 'enhance output/test/', 'estimate test.json']
for cmd in test_commands:
    args = main_parser.parse_args(cmd.split())
    assert args.command is not None
```

## Next Steps


---

*Source: test_cli_parsers.py:106 | Complexity: Intermediate | Last updated: 2026-02-14*