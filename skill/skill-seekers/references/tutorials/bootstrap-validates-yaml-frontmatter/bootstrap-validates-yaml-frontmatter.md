# How To: Bootstrap Validates Yaml Frontmatter

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: Verify generated SKILL.md has valid YAML frontmatter

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `subprocess`
- `sys`
- `pathlib`
- `pytest`
- `skill_seekers.cli.adaptors`

**Setup Required:**
```python
# Fixtures: run_bootstrap, output_skill_dir
```

## Step-by-Step Guide

### Step 1: 'Verify generated SKILL.md has valid YAML frontmatter'

```python
'Verify generated SKILL.md has valid YAML frontmatter'
```

**Verification:**
```python
assert result.returncode == 0
```

### Step 2: Assign result = run_bootstrap(...)

```python
result = run_bootstrap()
```

**Verification:**
```python
assert content.startswith('---'), 'Missing frontmatter start'
```

### Step 3: Assign content = unknown.read_text(...)

```python
content = (output_skill_dir / 'SKILL.md').read_text()
```

**Verification:**
```python
assert closing_found, 'Missing frontmatter closing delimiter'
```

### Step 4: Assign lines = content.split(...)

```python
lines = content.split('\n')
```

**Verification:**
```python
assert 'name:' in content[:500], 'Missing name field'
```

### Step 5: Assign closing_found = False

```python
closing_found = False
```

**Verification:**
```python
assert 'description:' in content[:500], 'Missing description field'
```

### Step 6: Assign closing_found = True

```python
closing_found = True
```


## Complete Example

```python
# Setup
# Fixtures: run_bootstrap, output_skill_dir

# Workflow
'Verify generated SKILL.md has valid YAML frontmatter'
result = run_bootstrap()
assert result.returncode == 0
content = (output_skill_dir / 'SKILL.md').read_text()
assert content.startswith('---'), 'Missing frontmatter start'
lines = content.split('\n')
closing_found = False
for _i, line in enumerate(lines[1:], 1):
    if line.strip() == '---':
        closing_found = True
        break
assert closing_found, 'Missing frontmatter closing delimiter'
assert 'name:' in content[:500], 'Missing name field'
assert 'description:' in content[:500], 'Missing description field'
```

## Next Steps


---

*Source: test_bootstrap_skill_e2e.py:85 | Complexity: Intermediate | Last updated: 2026-02-14*