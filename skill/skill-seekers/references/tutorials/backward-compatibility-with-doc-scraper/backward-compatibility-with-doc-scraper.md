# How To: Backward Compatibility With Doc Scraper

**Difficulty**: Intermediate
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: Test that detector can be used as drop-in replacement

## Prerequisites

**Required Modules:**
- `pytest`
- `bs4`
- `skill_seekers.cli.language_detector`


## Step-by-Step Guide

### Step 1: 'Test that detector can be used as drop-in replacement'

```python
'Test that detector can be used as drop-in replacement'
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
assert isinstance(confidence, float)
```

### Step 3: Assign html = '<code class="language-python">import os\nprint("hello")</code>'

```python
html = '<code class="language-python">import os\nprint("hello")</code>'
```

**Verification:**
```python
assert lang == 'python'
```

### Step 4: Assign soup = BeautifulSoup(...)

```python
soup = BeautifulSoup(html, 'html.parser')
```

**Verification:**
```python
assert 0.0 <= confidence <= 1.0
```

### Step 5: Assign elem = soup.find(...)

```python
elem = soup.find('code')
```

### Step 6: Assign code = elem.get_text(...)

```python
code = elem.get_text()
```

### Step 7: Assign unknown = detector.detect_from_html(...)

```python
lang, confidence = detector.detect_from_html(elem, code)
```

**Verification:**
```python
assert isinstance(lang, str)
```


## Complete Example

```python
# Workflow
'Test that detector can be used as drop-in replacement'
detector = LanguageDetector()
html = '<code class="language-python">import os\nprint("hello")</code>'
soup = BeautifulSoup(html, 'html.parser')
elem = soup.find('code')
code = elem.get_text()
lang, confidence = detector.detect_from_html(elem, code)
assert isinstance(lang, str)
assert isinstance(confidence, float)
assert lang == 'python'
assert 0.0 <= confidence <= 1.0
```

## Next Steps


---

*Source: test_language_detector.py:688 | Complexity: Intermediate | Last updated: 2026-02-14*