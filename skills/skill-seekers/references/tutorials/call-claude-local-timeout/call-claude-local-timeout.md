# How To: Call Claude Local Timeout

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: Test LOCAL mode timeout handling

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `json`
- `os`
- `unittest.mock`
- `pytest`
- `skill_seekers.cli.guide_enhancer`
- `subprocess`

**Setup Required:**
```python
# Fixtures: mock_run
```

## Step-by-Step Guide

### Step 1: 'Test LOCAL mode timeout handling'

```python
'Test LOCAL mode timeout handling'
```

**Verification:**
```python
assert result is None
```

### Step 2: Assign mock_run.side_effect = TimeoutExpired(...)

```python
mock_run.side_effect = TimeoutExpired('claude', 300)
```

### Step 3: Assign enhancer = GuideEnhancer(...)

```python
enhancer = GuideEnhancer(mode='local')
```

### Step 4: Assign prompt = 'Test prompt'

```python
prompt = 'Test prompt'
```

### Step 5: Assign result = enhancer._call_claude_local(...)

```python
result = enhancer._call_claude_local(prompt)
```

**Verification:**
```python
assert result is None
```


## Complete Example

```python
# Setup
# Fixtures: mock_run

# Workflow
'Test LOCAL mode timeout handling'
from subprocess import TimeoutExpired
mock_run.side_effect = TimeoutExpired('claude', 300)
enhancer = GuideEnhancer(mode='local')
if enhancer.mode == 'local':
    prompt = 'Test prompt'
    result = enhancer._call_claude_local(prompt)
    assert result is None
```

## Next Steps


---

*Source: test_guide_enhancer.py:495 | Complexity: Intermediate | Last updated: 2026-02-14*