# How To: Analyze Parser Arguments

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: Test AnalyzeParser has correct arguments.

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

### Step 1: 'Test AnalyzeParser has correct arguments.'

```python
'Test AnalyzeParser has correct arguments.'
```

**Verification:**
```python
assert args.command == 'analyze'
```

### Step 2: Assign main_parser = argparse.ArgumentParser(...)

```python
main_parser = argparse.ArgumentParser()
```

**Verification:**
```python
assert args.directory == '.'
```

### Step 3: Assign subparsers = main_parser.add_subparsers(...)

```python
subparsers = main_parser.add_subparsers(dest='command')
```

**Verification:**
```python
assert args.quick is True
```

### Step 4: Assign analyze_parser = AnalyzeParser(...)

```python
analyze_parser = AnalyzeParser()
```

**Verification:**
```python
assert args.comprehensive is True
```

### Step 5: Call analyze_parser.create_parser()

```python
analyze_parser.create_parser(subparsers)
```

**Verification:**
```python
assert args.skip_patterns is True
```

### Step 6: Assign args = main_parser.parse_args(...)

```python
args = main_parser.parse_args(['analyze', '--directory', '.'])
```

**Verification:**
```python
assert args.command == 'analyze'
```

### Step 7: Assign args = main_parser.parse_args(...)

```python
args = main_parser.parse_args(['analyze', '--directory', '.', '--quick'])
```

**Verification:**
```python
assert args.quick is True
```

### Step 8: Assign args = main_parser.parse_args(...)

```python
args = main_parser.parse_args(['analyze', '--directory', '.', '--comprehensive'])
```

**Verification:**
```python
assert args.comprehensive is True
```

### Step 9: Assign args = main_parser.parse_args(...)

```python
args = main_parser.parse_args(['analyze', '--directory', '.', '--skip-patterns'])
```

**Verification:**
```python
assert args.skip_patterns is True
```


## Complete Example

```python
# Workflow
'Test AnalyzeParser has correct arguments.'
main_parser = argparse.ArgumentParser()
subparsers = main_parser.add_subparsers(dest='command')
from skill_seekers.cli.parsers.analyze_parser import AnalyzeParser
analyze_parser = AnalyzeParser()
analyze_parser.create_parser(subparsers)
args = main_parser.parse_args(['analyze', '--directory', '.'])
assert args.command == 'analyze'
assert args.directory == '.'
args = main_parser.parse_args(['analyze', '--directory', '.', '--quick'])
assert args.quick is True
args = main_parser.parse_args(['analyze', '--directory', '.', '--comprehensive'])
assert args.comprehensive is True
args = main_parser.parse_args(['analyze', '--directory', '.', '--skip-patterns'])
assert args.skip_patterns is True
```

## Next Steps


---

*Source: test_cli_parsers.py:186 | Complexity: Advanced | Last updated: 2026-02-14*