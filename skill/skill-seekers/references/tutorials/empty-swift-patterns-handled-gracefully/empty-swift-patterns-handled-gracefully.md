# How To: Empty Swift Patterns Handled Gracefully

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: Test that empty SWIFT_PATTERNS dict doesn't crash detection

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

### Step 1: "Test that empty SWIFT_PATTERNS dict doesn't crash detection"

```python
"Test that empty SWIFT_PATTERNS dict doesn't crash detection"
```

**Verification:**
```python
assert isinstance(lang, str)
```

### Step 2: Assign detector = LanguageDetector(...)

```python
detector = LanguageDetector()
```

**Verification:**
```python
assert isinstance(confidence, (int, float))
```

### Step 3: Assign code = 'import SwiftUI\nstruct MyView: View { }'

```python
code = 'import SwiftUI\nstruct MyView: View { }'
```

### Step 4: Assign unknown = detector.detect_from_code(...)

```python
lang, confidence = detector.detect_from_code(code)
```

**Verification:**
```python
assert isinstance(lang, str)
```


## Complete Example

```python
# Workflow
"Test that empty SWIFT_PATTERNS dict doesn't crash detection"
import sys
from unittest.mock import patch
for mod in list(sys.modules.keys()):
    if 'skill_seekers.cli' in mod:
        del sys.modules[mod]
with patch.dict('sys.modules', {'skill_seekers.cli.swift_patterns': type('MockModule', (), {'SWIFT_PATTERNS': {}})}):
    from skill_seekers.cli.language_detector import LanguageDetector
    detector = LanguageDetector()
    code = 'import SwiftUI\nstruct MyView: View { }'
    lang, confidence = detector.detect_from_code(code)
    assert isinstance(lang, str)
    assert isinstance(confidence, (int, float))
```

## Next Steps


---

*Source: test_swift_detection.py:1323 | Complexity: Intermediate | Last updated: 2026-02-14*