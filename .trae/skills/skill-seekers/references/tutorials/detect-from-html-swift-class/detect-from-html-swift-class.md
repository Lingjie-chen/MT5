# How To: Detect From Html Swift Class

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: Test HTML element with Swift CSS class

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

### Step 1: 'Test HTML element with Swift CSS class'

```python
'Test HTML element with Swift CSS class'
```

**Verification:**
```python
assert lang == 'swift'
```

### Step 2: Assign detector = LanguageDetector(...)

```python
detector = LanguageDetector()
```

**Verification:**
```python
assert confidence == 1.0
```

### Step 3: Assign html = '<code class="language-swift">let x = 5</code>'

```python
html = '<code class="language-swift">let x = 5</code>'
```

### Step 4: Assign soup = BeautifulSoup(...)

```python
soup = BeautifulSoup(html, 'html.parser')
```

### Step 5: Assign elem = soup.find(...)

```python
elem = soup.find('code')
```

### Step 6: Assign unknown = detector.detect_from_html(...)

```python
lang, confidence = detector.detect_from_html(elem, 'let x = 5')
```

**Verification:**
```python
assert lang == 'swift'
```


## Complete Example

```python
# Workflow
'Test HTML element with Swift CSS class'
detector = LanguageDetector()
html = '<code class="language-swift">let x = 5</code>'
soup = BeautifulSoup(html, 'html.parser')
elem = soup.find('code')
lang, confidence = detector.detect_from_html(elem, 'let x = 5')
assert lang == 'swift'
assert confidence == 1.0
```

## Next Steps


---

*Source: test_swift_detection.py:44 | Complexity: Intermediate | Last updated: 2026-02-14*