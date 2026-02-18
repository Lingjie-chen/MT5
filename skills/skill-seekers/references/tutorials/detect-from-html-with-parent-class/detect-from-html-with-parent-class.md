# How To: Detect From Html With Parent Class

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: Test parent <pre> element with CSS class

## Prerequisites

**Required Modules:**
- `pytest`
- `bs4`
- `skill_seekers.cli.language_detector`


## Step-by-Step Guide

### Step 1: 'Test parent <pre> element with CSS class'

```python
'Test parent <pre> element with CSS class'
```

**Verification:**
```python
assert lang == 'java'
```

### Step 2: Assign detector = LanguageDetector(...)

```python
detector = LanguageDetector()
```

**Verification:**
```python
assert confidence == 1.0
```

### Step 3: Assign html = '<pre class="language-java"><code>System.out.println("hello");</code></pre>'

```python
html = '<pre class="language-java"><code>System.out.println("hello");</code></pre>'
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
lang, confidence = detector.detect_from_html(elem, 'System.out.println("hello");')
```

**Verification:**
```python
assert lang == 'java'
```


## Complete Example

```python
# Workflow
'Test parent <pre> element with CSS class'
detector = LanguageDetector()
html = '<pre class="language-java"><code>System.out.println("hello");</code></pre>'
soup = BeautifulSoup(html, 'html.parser')
elem = soup.find('code')
lang, confidence = detector.detect_from_html(elem, 'System.out.println("hello");')
assert lang == 'java'
assert confidence == 1.0
```

## Next Steps


---

*Source: test_language_detector.py:90 | Complexity: Intermediate | Last updated: 2026-02-14*