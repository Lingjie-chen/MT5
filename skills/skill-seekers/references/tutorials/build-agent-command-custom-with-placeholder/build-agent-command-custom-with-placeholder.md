# How To: Build Agent Command Custom With Placeholder

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: Test custom command with {prompt_file} placeholder.

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `pytest`
- `skill_seekers.cli.enhance_skill_local`

**Setup Required:**
```python
# Fixtures: tmp_path, monkeypatch
```

## Step-by-Step Guide

### Step 1: 'Test custom command with {prompt_file} placeholder.'

```python
'Test custom command with {prompt_file} placeholder.'
```

**Verification:**
```python
assert cmd_parts[0] == 'my-agent'
```

### Step 2: Call _allow_executable()

```python
_allow_executable(monkeypatch, name='my-agent')
```

**Verification:**
```python
assert '--input' in cmd_parts
```

### Step 3: Assign skill_dir = _make_skill_dir(...)

```python
skill_dir = _make_skill_dir(tmp_path)
```

**Verification:**
```python
assert prompt_file in cmd_parts
```

### Step 4: Assign enhancer = LocalSkillEnhancer(...)

```python
enhancer = LocalSkillEnhancer(skill_dir, agent='custom', agent_cmd='my-agent --input {prompt_file}')
```

**Verification:**
```python
assert uses_file is True
```

### Step 5: Assign prompt_file = str(...)

```python
prompt_file = str(tmp_path / 'prompt.txt')
```

### Step 6: Assign unknown = enhancer._build_agent_command(...)

```python
cmd_parts, uses_file = enhancer._build_agent_command(prompt_file, False)
```

**Verification:**
```python
assert cmd_parts[0] == 'my-agent'
```


## Complete Example

```python
# Setup
# Fixtures: tmp_path, monkeypatch

# Workflow
'Test custom command with {prompt_file} placeholder.'
_allow_executable(monkeypatch, name='my-agent')
skill_dir = _make_skill_dir(tmp_path)
enhancer = LocalSkillEnhancer(skill_dir, agent='custom', agent_cmd='my-agent --input {prompt_file}')
prompt_file = str(tmp_path / 'prompt.txt')
cmd_parts, uses_file = enhancer._build_agent_command(prompt_file, False)
assert cmd_parts[0] == 'my-agent'
assert '--input' in cmd_parts
assert prompt_file in cmd_parts
assert uses_file is True
```

## Next Steps


---

*Source: test_enhance_skill_local.py:59 | Complexity: Intermediate | Last updated: 2026-02-14*