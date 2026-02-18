# How To: Build Agent Command Claude

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: Test Claude Code command building.

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

### Step 1: 'Test Claude Code command building.'

```python
'Test Claude Code command building.'
```

**Verification:**
```python
assert cmd_parts[0] == 'claude'
```

### Step 2: Assign skill_dir = _make_skill_dir(...)

```python
skill_dir = _make_skill_dir(tmp_path)
```

**Verification:**
```python
assert '--dangerously-skip-permissions' in cmd_parts
```

### Step 3: Assign enhancer = LocalSkillEnhancer(...)

```python
enhancer = LocalSkillEnhancer(skill_dir, agent='claude')
```

**Verification:**
```python
assert prompt_file in cmd_parts
```

### Step 4: Assign prompt_file = str(...)

```python
prompt_file = str(tmp_path / 'prompt.txt')
```

**Verification:**
```python
assert uses_file is True
```

### Step 5: Assign unknown = enhancer._build_agent_command(...)

```python
cmd_parts, uses_file = enhancer._build_agent_command(prompt_file, True)
```

**Verification:**
```python
assert cmd_parts[0] == 'claude'
```


## Complete Example

```python
# Setup
# Fixtures: tmp_path

# Workflow
'Test Claude Code command building.'
skill_dir = _make_skill_dir(tmp_path)
enhancer = LocalSkillEnhancer(skill_dir, agent='claude')
prompt_file = str(tmp_path / 'prompt.txt')
cmd_parts, uses_file = enhancer._build_agent_command(prompt_file, True)
assert cmd_parts[0] == 'claude'
assert '--dangerously-skip-permissions' in cmd_parts
assert prompt_file in cmd_parts
assert uses_file is True
```

## Next Steps


---

*Source: test_enhance_skill_local.py:32 | Complexity: Intermediate | Last updated: 2026-02-14*