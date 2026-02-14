# How To: Unity Lifecycle Methods

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: Test Unity lifecycle method detection

## Prerequisites

**Required Modules:**
- `pytest`
- `bs4`
- `skill_seekers.cli.language_detector`


## Step-by-Step Guide

### Step 1: 'Test Unity lifecycle method detection'

```python
'Test Unity lifecycle method detection'
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

### Step 3: Assign code = '\n        void Awake() { }\n        void Start() { }\n        void Update() { }\n        void FixedUpdate() { }\n        void LateUpdate() { }\n        '

```python
code = '\n        void Awake() { }\n        void Start() { }\n        void Update() { }\n        void FixedUpdate() { }\n        void LateUpdate() { }\n        '
```

### Step 4: Assign unknown = detector.detect_from_code(...)

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
'Test Unity lifecycle method detection'
detector = LanguageDetector()
code = '\n        void Awake() { }\n        void Start() { }\n        void Update() { }\n        void FixedUpdate() { }\n        void LateUpdate() { }\n        '
lang, confidence = detector.detect_from_code(code)
assert lang == 'csharp'
assert confidence >= 0.5
```

## Next Steps


---

*Source: test_language_detector.py:128 | Complexity: Intermediate | Last updated: 2026-02-14*