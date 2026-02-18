# How To: Github Parser Arguments

**Difficulty**: Intermediate
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: Test GitHubParser has correct arguments.

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

### Step 1: 'Test GitHubParser has correct arguments.'

```python
'Test GitHubParser has correct arguments.'
```

**Verification:**
```python
assert args.command == 'github'
```

### Step 2: Assign main_parser = argparse.ArgumentParser(...)

```python
main_parser = argparse.ArgumentParser()
```

**Verification:**
```python
assert args.repo == 'owner/repo'
```

### Step 3: Assign subparsers = main_parser.add_subparsers(...)

```python
subparsers = main_parser.add_subparsers(dest='command')
```

**Verification:**
```python
assert args.non_interactive is True
```

### Step 4: Assign github_parser = GitHubParser(...)

```python
github_parser = GitHubParser()
```

### Step 5: Call github_parser.create_parser()

```python
github_parser.create_parser(subparsers)
```

### Step 6: Assign args = main_parser.parse_args(...)

```python
args = main_parser.parse_args(['github', '--repo', 'owner/repo'])
```

**Verification:**
```python
assert args.command == 'github'
```

### Step 7: Assign args = main_parser.parse_args(...)

```python
args = main_parser.parse_args(['github', '--repo', 'owner/repo', '--non-interactive'])
```

**Verification:**
```python
assert args.non_interactive is True
```


## Complete Example

```python
# Workflow
'Test GitHubParser has correct arguments.'
main_parser = argparse.ArgumentParser()
subparsers = main_parser.add_subparsers(dest='command')
github_parser = GitHubParser()
github_parser.create_parser(subparsers)
args = main_parser.parse_args(['github', '--repo', 'owner/repo'])
assert args.command == 'github'
assert args.repo == 'owner/repo'
args = main_parser.parse_args(['github', '--repo', 'owner/repo', '--non-interactive'])
assert args.non_interactive is True
```

## Next Steps


---

*Source: test_cli_parsers.py:153 | Complexity: Intermediate | Last updated: 2026-02-14*