# How To: Package Parser Arguments

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: Test PackageParser has correct arguments.

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

### Step 1: 'Test PackageParser has correct arguments.'

```python
'Test PackageParser has correct arguments.'
```

**Verification:**
```python
assert args.command == 'package'
```

### Step 2: Assign main_parser = argparse.ArgumentParser(...)

```python
main_parser = argparse.ArgumentParser()
```

**Verification:**
```python
assert args.skill_directory == 'output/test/'
```

### Step 3: Assign subparsers = main_parser.add_subparsers(...)

```python
subparsers = main_parser.add_subparsers(dest='command')
```

**Verification:**
```python
assert args.target == 'gemini'
```

### Step 4: Assign package_parser = PackageParser(...)

```python
package_parser = PackageParser()
```

**Verification:**
```python
assert args.no_open is True
```

### Step 5: Call package_parser.create_parser()

```python
package_parser.create_parser(subparsers)
```

### Step 6: Assign args = main_parser.parse_args(...)

```python
args = main_parser.parse_args(['package', 'output/test/'])
```

**Verification:**
```python
assert args.command == 'package'
```

### Step 7: Assign args = main_parser.parse_args(...)

```python
args = main_parser.parse_args(['package', 'output/test/', '--target', 'gemini'])
```

**Verification:**
```python
assert args.target == 'gemini'
```

### Step 8: Assign args = main_parser.parse_args(...)

```python
args = main_parser.parse_args(['package', 'output/test/', '--no-open'])
```

**Verification:**
```python
assert args.no_open is True
```


## Complete Example

```python
# Workflow
'Test PackageParser has correct arguments.'
main_parser = argparse.ArgumentParser()
subparsers = main_parser.add_subparsers(dest='command')
package_parser = PackageParser()
package_parser.create_parser(subparsers)
args = main_parser.parse_args(['package', 'output/test/'])
assert args.command == 'package'
assert args.skill_directory == 'output/test/'
args = main_parser.parse_args(['package', 'output/test/', '--target', 'gemini'])
assert args.target == 'gemini'
args = main_parser.parse_args(['package', 'output/test/', '--no-open'])
assert args.no_open is True
```

## Next Steps


---

*Source: test_cli_parsers.py:168 | Complexity: Advanced | Last updated: 2026-02-14*