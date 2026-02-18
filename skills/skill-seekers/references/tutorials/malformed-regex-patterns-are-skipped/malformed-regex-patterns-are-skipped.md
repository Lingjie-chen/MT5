# How To: Malformed Regex Patterns Are Skipped

**Difficulty**: Advanced
**Estimated Time**: 10 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: Test that invalid regex patterns are logged and skipped without crashing

## Prerequisites

**Required Modules:**
- `pytest`
- `bs4`
- `skill_seekers.cli.language_detector`
- `skill_seekers.cli.swift_patterns`
- `skill_seekers.cli.swift_patterns`
- `skill_seekers.cli.swift_patterns`
- `unittest.mock`
- `skill_seekers.cli.language_detector`
- `sys`
- `unittest.mock`
- `unittest.mock`
- `skill_seekers.cli.language_detector`
- `inspect`
- `skill_seekers.cli`
- `skill_seekers.cli.language_detector`
- `skill_seekers.cli.language_detector`
- `skill_seekers.cli.language_detector`


## Step-by-Step Guide

### Step 1: 'Test that invalid regex patterns are logged and skipped without crashing'

```python
'Test that invalid regex patterns are logged and skipped without crashing'
```

**Verification:**
```python
assert any(('Invalid regex pattern' in str(call) for call in mock_logger.error.call_args_list)), 'Expected error log for malformed pattern'
```

### Step 2: Assign original_patterns = ld_module.LANGUAGE_PATTERNS.copy(...)

```python
original_patterns = ld_module.LANGUAGE_PATTERNS.copy()
```

### Step 3: Assign unknown = value

```python
ld_module.LANGUAGE_PATTERNS['test_malformed'] = [('(?P<invalid)', 5), ('valid_pattern', 3)]
```

### Step 4: Assign _detector = LanguageDetector(...)

```python
_detector = LanguageDetector()
```

**Verification:**
```python
assert any(('Invalid regex pattern' in str(call) for call in mock_logger.error.call_args_list)), 'Expected error log for malformed pattern'
```

### Step 5: Assign ld_module.LANGUAGE_PATTERNS = original_patterns

```python
ld_module.LANGUAGE_PATTERNS = original_patterns
```


## Complete Example

```python
# Workflow
'Test that invalid regex patterns are logged and skipped without crashing'
from unittest.mock import patch
from skill_seekers.cli.language_detector import LanguageDetector
with patch('skill_seekers.cli.language_detector.logger') as mock_logger:
    import skill_seekers.cli.language_detector as ld_module
    original_patterns = ld_module.LANGUAGE_PATTERNS.copy()
    try:
        ld_module.LANGUAGE_PATTERNS['test_malformed'] = [('(?P<invalid)', 5), ('valid_pattern', 3)]
        _detector = LanguageDetector()
        assert any(('Invalid regex pattern' in str(call) for call in mock_logger.error.call_args_list)), 'Expected error log for malformed pattern'
    finally:
        ld_module.LANGUAGE_PATTERNS = original_patterns
```

## Next Steps


---

*Source: test_swift_detection.py:1289 | Complexity: Advanced | Last updated: 2026-02-14*