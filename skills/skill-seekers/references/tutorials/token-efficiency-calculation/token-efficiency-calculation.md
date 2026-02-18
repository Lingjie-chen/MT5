# How To: Token Efficiency Calculation

**Difficulty**: Advanced
**Estimated Time**: 20 minutes
**Tags**: workflow, integration

## Overview

Workflow: Calculate token efficiency with GitHub overhead.

## Prerequisites

**Required Modules:**
- `json`
- `pathlib`
- `unittest.mock`
- `pytest`
- `skill_seekers.cli.generate_router`
- `skill_seekers.cli.github_fetcher`
- `skill_seekers.cli.merge_sources`
- `skill_seekers.cli.unified_codebase_analyzer`


## Step-by-Step Guide

### Step 1: 'Calculate token efficiency with GitHub overhead.'

```python
'Calculate token efficiency with GitHub overhead.'
```

**Verification:**
```python
assert reduction_percent >= 29, f'Token reduction {reduction_percent:.1f}% below 29% (conservative target)'
```

### Step 2: Assign monolithic_size = value

```python
monolithic_size = 666 + 50
```

### Step 3: Assign router_size = value

```python
router_size = 150 + 50
```

### Step 4: Assign avg_subskill_size = value

```python
avg_subskill_size = (250 + 200 + 250 + 400) / 4
```

### Step 5: Assign avg_subskill_with_github = value

```python
avg_subskill_with_github = avg_subskill_size + 30
```

### Step 6: Assign avg_router_query = value

```python
avg_router_query = router_size + avg_subskill_with_github
```

### Step 7: Assign reduction = value

```python
reduction = (monolithic_size - avg_router_query) / monolithic_size
```

### Step 8: Assign reduction_percent = value

```python
reduction_percent = reduction * 100
```

### Step 9: Call print()

```python
print('\n=== Token Efficiency Calculation ===')
```

### Step 10: Call print()

```python
print(f'Monolithic: {monolithic_size} lines')
```

### Step 11: Call print()

```python
print(f'Router: {router_size} lines')
```

### Step 12: Call print()

```python
print(f'Avg Sub-skill: {avg_subskill_with_github} lines')
```

### Step 13: Call print()

```python
print(f'Avg Query: {avg_router_query} lines')
```

### Step 14: Call print()

```python
print(f'Reduction: {reduction_percent:.1f}%')
```

### Step 15: Call print()

```python
print('Target: 35-40%')
```

**Verification:**
```python
assert reduction_percent >= 29, f'Token reduction {reduction_percent:.1f}% below 29% (conservative target)'
```


## Complete Example

```python
# Workflow
'Calculate token efficiency with GitHub overhead.'
monolithic_size = 666 + 50
router_size = 150 + 50
avg_subskill_size = (250 + 200 + 250 + 400) / 4
avg_subskill_with_github = avg_subskill_size + 30
avg_router_query = router_size + avg_subskill_with_github
reduction = (monolithic_size - avg_router_query) / monolithic_size
reduction_percent = reduction * 100
print('\n=== Token Efficiency Calculation ===')
print(f'Monolithic: {monolithic_size} lines')
print(f'Router: {router_size} lines')
print(f'Avg Sub-skill: {avg_subskill_with_github} lines')
print(f'Avg Query: {avg_router_query} lines')
print(f'Reduction: {reduction_percent:.1f}%')
print('Target: 35-40%')
assert reduction_percent >= 29, f'Token reduction {reduction_percent:.1f}% below 29% (conservative target)'
```

## Next Steps


---

*Source: test_architecture_scenarios.py:1025 | Complexity: Advanced | Last updated: 2026-02-14*