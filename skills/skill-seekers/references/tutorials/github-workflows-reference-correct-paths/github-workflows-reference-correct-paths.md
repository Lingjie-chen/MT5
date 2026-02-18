# How To: Github Workflows Reference Correct Paths

**Difficulty**: Beginner
**Estimated Time**: 5 minutes
**Tags**: workflow, integration

## Overview

Workflow: Test that GitHub workflows reference correct MCP paths

## Prerequisites

**Required Modules:**
- `re`
- `subprocess`
- `pathlib`
- `pytest`
- `re`
- `re`
- `os`


## Step-by-Step Guide

### Step 1: 'Test that GitHub workflows reference correct MCP paths'

```python
'Test that GitHub workflows reference correct MCP paths'
```

**Verification:**
```python
assert 'mcp/requirements.txt' not in content or 'skill_seeker_mcp/requirements.txt' in content, 'GitHub workflow should use correct MCP paths'
```

### Step 2: Assign workflow_file = Path(...)

```python
workflow_file = Path('.github/workflows/tests.yml')
```

**Verification:**
```python
assert 'mcp/requirements.txt' not in content or 'skill_seeker_mcp/requirements.txt' in content, 'GitHub workflow should use correct MCP paths'
```

### Step 3: Assign content = f.read(...)

```python
content = f.read()
```


## Complete Example

```python
# Workflow
'Test that GitHub workflows reference correct MCP paths'
workflow_file = Path('.github/workflows/tests.yml')
if workflow_file.exists():
    with open(workflow_file) as f:
        content = f.read()
    assert 'mcp/requirements.txt' not in content or 'skill_seeker_mcp/requirements.txt' in content, 'GitHub workflow should use correct MCP paths'
```

## Next Steps


---

*Source: test_setup_scripts.py:200 | Complexity: Beginner | Last updated: 2026-02-14*