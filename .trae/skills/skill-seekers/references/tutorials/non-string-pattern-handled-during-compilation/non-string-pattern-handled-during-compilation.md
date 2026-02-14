# How To: Non String Pattern Handled During Compilation

**Difficulty**: Advanced
**Estimated Time**: 10 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: Test that non-string patterns are caught during compilation

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

### Step 1: 'Test that non-string patterns are caught during compilation'

```python
'Test that non-string patterns are caught during compilation'
```

**Verification:**
```python
assert any(('not a string' in str(call) for call in mock_logger.error.call_args_list)), 'Expected error log for non-string pattern'
```

### Step 2: Assign original = ld_module.LANGUAGE_PATTERNS.copy(...)

```python
original = ld_module.LANGUAGE_PATTERNS.copy()
```

### Step 3: Assign unknown = value

```python
ld_module.LANGUAGE_PATTERNS['test_nonstring'] = [(None, 5)]
```

### Step 4: Assign _detector = LanguageDetector(...)

```python
_detector = LanguageDetector()
```

**Verification:**
```python
assert any(('not a string' in str(call) for call in mock_logger.error.call_args_list)), 'Expected error log for non-string pattern'
```

### Step 5: Assign ld_module.LANGUAGE_PATTERNS = original

```python
ld_module.LANGUAGE_PATTERNS = original
```


## Complete Example

```python
# Workflow
'Test that non-string patterns are caught during compilation'
from unittest.mock import patch
from skill_seekers.cli.language_detector import LanguageDetector
with patch('skill_seekers.cli.language_detector.logger') as mock_logger:
    import skill_seekers.cli.language_detector as ld_module
    original = ld_module.LANGUAGE_PATTERNS.copy()
    try:
        ld_module.LANGUAGE_PATTERNS['test_nonstring'] = [(None, 5)]
        _detector = LanguageDetector()
        assert any(('not a string' in str(call) for call in mock_logger.error.call_args_list)), 'Expected error log for non-string pattern'
    finally:
        ld_module.LANGUAGE_PATTERNS = original
```

## Next Steps


---

*Source: test_swift_detection.py:1351 | Complexity: Advanced | Last updated: 2026-02-14*