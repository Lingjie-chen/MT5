# How To: Summarize Reference Basic

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: Test basic summarization preserves structure

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

### Step 1: 'Test basic summarization preserves structure'

```python
'Test basic summarization preserves structure'
```

**Verification:**
```python
assert '# Introduction' in summarized
```

### Step 2: Assign enhancer = LocalSkillEnhancer(...)

```python
enhancer = LocalSkillEnhancer(tmp_path)
```

**Verification:**
```python
assert '```python' in summarized
```

### Step 3: Assign sections = value

```python
sections = []
```

**Verification:**
```python
assert '[Content intelligently summarized' in summarized
```

### Step 4: Assign content = value

```python
content = '# Introduction\n\nThis is the framework introduction.\n' + '\n'.join(sections)
```

**Verification:**
```python
assert len(summarized) < len(content)
```

### Step 5: Assign summarized = enhancer.summarize_reference(...)

```python
summarized = enhancer.summarize_reference(content, target_ratio=0.3)
```

**Verification:**
```python
assert '# Introduction' in summarized
```

### Step 6: Call sections.append()

```python
sections.append(f'\n## Section {i}\n\nThis is section {i} with detailed explanation that would benefit from summarization.\nWe add multiple paragraphs to make the content more realistic and substantial.\nThis content explains various aspects of the framework in detail.\n\nAnother paragraph with more information about this specific topic.\nTechnical details and explanations continue here with examples and use cases.\n\n```python\n# Example code for section {i}\ndef function_{i}():\n    print("Section {i}")\n    return {i}\n```\n\nFinal paragraph wrapping up this section with concluding remarks.\n')
```


## Complete Example

```python
# Setup
# Fixtures: tmp_path

# Workflow
'Test basic summarization preserves structure'
enhancer = LocalSkillEnhancer(tmp_path)
sections = []
for i in range(20):
    sections.append(f'\n## Section {i}\n\nThis is section {i} with detailed explanation that would benefit from summarization.\nWe add multiple paragraphs to make the content more realistic and substantial.\nThis content explains various aspects of the framework in detail.\n\nAnother paragraph with more information about this specific topic.\nTechnical details and explanations continue here with examples and use cases.\n\n```python\n# Example code for section {i}\ndef function_{i}():\n    print("Section {i}")\n    return {i}\n```\n\nFinal paragraph wrapping up this section with concluding remarks.\n')
content = '# Introduction\n\nThis is the framework introduction.\n' + '\n'.join(sections)
summarized = enhancer.summarize_reference(content, target_ratio=0.3)
assert '# Introduction' in summarized
assert '```python' in summarized
assert '[Content intelligently summarized' in summarized
assert len(summarized) < len(content)
```

## Next Steps


---

*Source: test_smart_summarization.py:16 | Complexity: Intermediate | Last updated: 2026-02-14*