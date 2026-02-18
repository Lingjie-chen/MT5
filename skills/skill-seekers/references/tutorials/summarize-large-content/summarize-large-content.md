# How To: Summarize Large Content

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: Test summarization with very large content

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

### Step 1: 'Test summarization with very large content'

```python
'Test summarization with very large content'
```

**Verification:**
```python
assert summarized_size < original_size
```

### Step 2: Assign enhancer = LocalSkillEnhancer(...)

```python
enhancer = LocalSkillEnhancer(tmp_path)
```

**Verification:**
```python
assert 0.2 <= ratio <= 0.5, f'Ratio {ratio:.2f} not in expected range'
```

### Step 3: Assign sections = value

```python
sections = []
```

### Step 4: Assign content = unknown.join(...)

```python
content = '\n'.join(sections)
```

### Step 5: Assign original_size = len(...)

```python
original_size = len(content)
```

### Step 6: Assign summarized = enhancer.summarize_reference(...)

```python
summarized = enhancer.summarize_reference(content, target_ratio=0.3)
```

### Step 7: Assign summarized_size = len(...)

```python
summarized_size = len(summarized)
```

**Verification:**
```python
assert summarized_size < original_size
```

### Step 8: Assign ratio = value

```python
ratio = summarized_size / original_size
```

**Verification:**
```python
assert 0.2 <= ratio <= 0.5, f'Ratio {ratio:.2f} not in expected range'
```

### Step 9: Call sections.append()

```python
sections.append(f'\n## Section {i}\n\nThis is section {i} with lots of content that needs to be summarized.\nWe add multiple paragraphs to make it realistic.\n\n```python\n# Code example {i}\ndef function_{i}():\n    return {i}\n```\n\nMore explanatory text follows here.\nAnother paragraph of content.\n')
```


## Complete Example

```python
# Setup
# Fixtures: tmp_path

# Workflow
'Test summarization with very large content'
enhancer = LocalSkillEnhancer(tmp_path)
sections = []
for i in range(50):
    sections.append(f'\n## Section {i}\n\nThis is section {i} with lots of content that needs to be summarized.\nWe add multiple paragraphs to make it realistic.\n\n```python\n# Code example {i}\ndef function_{i}():\n    return {i}\n```\n\nMore explanatory text follows here.\nAnother paragraph of content.\n')
content = '\n'.join(sections)
original_size = len(content)
summarized = enhancer.summarize_reference(content, target_ratio=0.3)
summarized_size = len(summarized)
assert summarized_size < original_size
ratio = summarized_size / original_size
assert 0.2 <= ratio <= 0.5, f'Ratio {ratio:.2f} not in expected range'
```

## Next Steps


---

*Source: test_smart_summarization.py:94 | Complexity: Advanced | Last updated: 2026-02-14*