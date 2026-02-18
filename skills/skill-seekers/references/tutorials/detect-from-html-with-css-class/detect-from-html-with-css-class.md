# How To: Detect From Html With Css Class

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: Test HTML element with CSS class

## Prerequisites

**Required Modules:**
- `pytest`
- `bs4`
- `skill_seekers.cli.language_detector`


## Step-by-Step Guide

### Step 1: 'Test HTML element with CSS class'

```python
'Test HTML element with CSS class'
```

**Verification:**
```python
assert lang == 'python'
```

### Step 2: Assign detector = LanguageDetector(...)

```python
detector = LanguageDetector()
```

**Verification:**
```python
assert confidence == 1.0
```

### Step 3: Assign html = '<code class="language-python">print("hello")</code>'

```python
html = '<code class="language-python">print("hello")</code>'
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
lang, confidence = detector.detect_from_html(elem, 'print("hello")')
```

**Verification:**
```python
assert lang == 'python'
```


## Complete Example

```python
# Workflow
'Test HTML element with CSS class'
detector = LanguageDetector()
html = '<code class="language-python">print("hello")</code>'
soup = BeautifulSoup(html, 'html.parser')
elem = soup.find('code')
lang, confidence = detector.detect_from_html(elem, 'print("hello")')
assert lang == 'python'
assert confidence == 1.0
```

## Next Steps


---

*Source: test_language_detector.py:77 | Complexity: Intermediate | Last updated: 2026-02-14*