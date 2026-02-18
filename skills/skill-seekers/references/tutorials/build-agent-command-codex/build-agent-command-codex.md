# How To: Build Agent Command Codex

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: Test Codex CLI command building.

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `pytest`
- `skill_seekers.cli.enhance_skill_local`

**Setup Required:**
```python
# Fixtures: tmp_path
```

## Step-by-Step Guide

### Step 1: 'Test Codex CLI command building.'

```python
'Test Codex CLI command building.'
```

**Verification:**
```python
assert cmd_parts[0] == 'codex'
```

### Step 2: Assign skill_dir = _make_skill_dir(...)

```python
skill_dir = _make_skill_dir(tmp_path)
```

**Verification:**
```python
assert 'exec' in cmd_parts
```

### Step 3: Assign enhancer = LocalSkillEnhancer(...)

```python
enhancer = LocalSkillEnhancer(skill_dir, agent='codex')
```

**Verification:**
```python
assert '--full-auto' in cmd_parts
```

### Step 4: Assign prompt_file = str(...)

```python
prompt_file = str(tmp_path / 'prompt.txt')
```

**Verification:**
```python
assert '--skip-git-repo-check' in cmd_parts
```

### Step 5: Assign unknown = enhancer._build_agent_command(...)

```python
cmd_parts, uses_file = enhancer._build_agent_command(prompt_file, False)
```

**Verification:**
```python
assert uses_file is False
```


## Complete Example

```python
# Setup
# Fixtures: tmp_path

# Workflow
'Test Codex CLI command building.'
skill_dir = _make_skill_dir(tmp_path)
enhancer = LocalSkillEnhancer(skill_dir, agent='codex')
prompt_file = str(tmp_path / 'prompt.txt')
cmd_parts, uses_file = enhancer._build_agent_command(prompt_file, False)
assert cmd_parts[0] == 'codex'
assert 'exec' in cmd_parts
assert '--full-auto' in cmd_parts
assert '--skip-git-repo-check' in cmd_parts
assert uses_file is False
```

## Next Steps


---

*Source: test_enhance_skill_local.py:45 | Complexity: Intermediate | Last updated: 2026-02-14*