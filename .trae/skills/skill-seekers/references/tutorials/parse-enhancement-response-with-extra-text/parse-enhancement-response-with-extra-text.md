# How To: Parse Enhancement Response With Extra Text

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: Test parsing JSON embedded in text

## Prerequisites

**Required Modules:**
- `json`
- `os`
- `unittest.mock`
- `pytest`
- `skill_seekers.cli.guide_enhancer`
- `subprocess`


## Step-by-Step Guide

### Step 1: 'Test parsing JSON embedded in text'

```python
'Test parsing JSON embedded in text'
```

**Verification:**
```python
assert 'title' in result
```

### Step 2: Assign enhancer = GuideEnhancer(...)

```python
enhancer = GuideEnhancer(mode='none')
```

### Step 3: Assign json_data = value

```python
json_data = {'step_descriptions': [], 'troubleshooting': [], 'prerequisites_detailed': [], 'next_steps': [], 'use_cases': []}
```

### Step 4: Assign response = value

```python
response = f"Here's the result:\n{json.dumps(json_data)}\nDone!"
```

### Step 5: Assign guide_data = value

```python
guide_data = {'title': 'Test', 'steps': [], 'language': 'python'}
```

### Step 6: Assign result = enhancer._parse_enhancement_response(...)

```python
result = enhancer._parse_enhancement_response(response, guide_data)
```

**Verification:**
```python
assert 'title' in result
```


## Complete Example

```python
# Workflow
'Test parsing JSON embedded in text'
enhancer = GuideEnhancer(mode='none')
json_data = {'step_descriptions': [], 'troubleshooting': [], 'prerequisites_detailed': [], 'next_steps': [], 'use_cases': []}
response = f"Here's the result:\n{json.dumps(json_data)}\nDone!"
guide_data = {'title': 'Test', 'steps': [], 'language': 'python'}
result = enhancer._parse_enhancement_response(response, guide_data)
assert 'title' in result
```

## Next Steps


---

*Source: test_guide_enhancer.py:585 | Complexity: Intermediate | Last updated: 2026-02-14*