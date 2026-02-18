# How To: Call Claude Local Success

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: Test successful LOCAL mode call

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

### Step 1: 'Test successful LOCAL mode call'

```python
'Test successful LOCAL mode call'
```

**Verification:**
```python
assert result is not None
```

### Step 2: Assign mock_run.return_value = MagicMock(...)

```python
mock_run.return_value = MagicMock(returncode=0, stdout=json.dumps({'step_descriptions': [], 'troubleshooting': [], 'prerequisites_detailed': [], 'next_steps': [], 'use_cases': []}))
```

**Verification:**
```python
assert mock_run.called
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
assert result is not None
```


## Complete Example

```python
# Setup
# Fixtures: mock_run

# Workflow
'Test successful LOCAL mode call'
mock_run.return_value = MagicMock(returncode=0, stdout=json.dumps({'step_descriptions': [], 'troubleshooting': [], 'prerequisites_detailed': [], 'next_steps': [], 'use_cases': []}))
enhancer = GuideEnhancer(mode='local')
if enhancer.mode == 'local':
    prompt = 'Test prompt'
    result = enhancer._call_claude_local(prompt)
    assert result is not None
    assert mock_run.called
```

## Next Steps


---

*Source: test_guide_enhancer.py:471 | Complexity: Intermediate | Last updated: 2026-02-14*