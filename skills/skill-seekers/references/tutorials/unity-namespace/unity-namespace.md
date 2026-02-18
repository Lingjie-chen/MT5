# How To: Unity Namespace

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: Test Unity namespace detection

## Prerequisites

**Required Modules:**
- `pytest`
- `bs4`
- `skill_seekers.cli.language_detector`


## Step-by-Step Guide

### Step 1: 'Test Unity namespace detection'

```python
'Test Unity namespace detection'
```

**Verification:**
```python
assert lang == 'csharp'
```

### Step 2: Assign detector = LanguageDetector(...)

```python
detector = LanguageDetector()
```

**Verification:**
```python
assert confidence >= 0.5
```

### Step 3: Assign code = 'using UnityEngine;'

```python
code = 'using UnityEngine;'
```

**Verification:**
```python
assert lang == 'csharp'
```

### Step 4: Assign unknown = detector.detect_from_code(...)

```python
lang, confidence = detector.detect_from_code(code)
```

**Verification:**
```python
assert confidence >= 0.5
```

### Step 5: Assign code = '\n        using UnityEngine;\n        using System.Collections;\n        '

```python
code = '\n        using UnityEngine;\n        using System.Collections;\n        '
```

### Step 6: Assign unknown = detector.detect_from_code(...)

```python
lang, confidence = detector.detect_from_code(code)
```

**Verification:**
```python
assert lang == 'csharp'
```


## Complete Example

```python
# Workflow
'Test Unity namespace detection'
detector = LanguageDetector()
code = 'using UnityEngine;'
lang, confidence = detector.detect_from_code(code)
assert lang == 'csharp'
assert confidence >= 0.5
code = '\n        using UnityEngine;\n        using System.Collections;\n        '
lang, confidence = detector.detect_from_code(code)
assert lang == 'csharp'
assert confidence >= 0.5
```

## Next Steps


---

*Source: test_language_detector.py:190 | Complexity: Intermediate | Last updated: 2026-02-14*