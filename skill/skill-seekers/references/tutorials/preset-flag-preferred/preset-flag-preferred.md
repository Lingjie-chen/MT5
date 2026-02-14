# How To: Preset Flag Preferred

**Difficulty**: Intermediate
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: Test that --preset flag is the recommended way.

## Prerequisites

**Required Modules:**
- `pytest`
- `skill_seekers.cli.presets`
- `skill_seekers.cli.codebase_scraper`
- `argparse`
- `skill_seekers.cli.codebase_scraper`
- `argparse`
- `skill_seekers.cli.codebase_scraper`
- `argparse`
- `skill_seekers.cli.codebase_scraper`
- `argparse`
- `skill_seekers.cli.codebase_scraper`
- `argparse`
- `skill_seekers.cli.codebase_scraper`
- `argparse`


## Step-by-Step Guide

### Step 1: 'Test that --preset flag is the recommended way.'

```python
'Test that --preset flag is the recommended way.'
```

**Verification:**
```python
assert updated['depth'] == 'surface'
```

### Step 2: Assign args = value

```python
args = {'preset': 'quick'}
```

**Verification:**
```python
assert updated['depth'] == 'deep'
```

### Step 3: Assign updated = PresetManager.apply_preset(...)

```python
updated = PresetManager.apply_preset('quick', args)
```

**Verification:**
```python
assert updated['depth'] == 'full'
```

### Step 4: Assign args = value

```python
args = {'preset': 'standard'}
```

### Step 5: Assign updated = PresetManager.apply_preset(...)

```python
updated = PresetManager.apply_preset('standard', args)
```

**Verification:**
```python
assert updated['depth'] == 'deep'
```

### Step 6: Assign args = value

```python
args = {'preset': 'comprehensive'}
```

### Step 7: Assign updated = PresetManager.apply_preset(...)

```python
updated = PresetManager.apply_preset('comprehensive', args)
```

**Verification:**
```python
assert updated['depth'] == 'full'
```


## Complete Example

```python
# Workflow
'Test that --preset flag is the recommended way.'
args = {'preset': 'quick'}
updated = PresetManager.apply_preset('quick', args)
assert updated['depth'] == 'surface'
args = {'preset': 'standard'}
updated = PresetManager.apply_preset('standard', args)
assert updated['depth'] == 'deep'
args = {'preset': 'comprehensive'}
updated = PresetManager.apply_preset('comprehensive', args)
assert updated['depth'] == 'full'
```

## Next Steps


---

*Source: test_preset_system.py:319 | Complexity: Intermediate | Last updated: 2026-02-14*