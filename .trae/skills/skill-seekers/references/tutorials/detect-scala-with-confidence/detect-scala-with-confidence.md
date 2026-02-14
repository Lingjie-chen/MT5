# How To: Detect Scala With Confidence

**Difficulty**: Intermediate
**Estimated Time**: 15 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: Test Scala detection

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `sys`
- `unittest`
- `pathlib`
- `fitz`
- `skill_seekers.cli.pdf_extractor_poc`
- `skill_seekers.cli.language_detector`
- `skill_seekers.cli.language_detector`
- `skill_seekers.cli.language_detector`
- `skill_seekers.cli.language_detector`
- `skill_seekers.cli.language_detector`
- `skill_seekers.cli.language_detector`
- `skill_seekers.cli.language_detector`
- `skill_seekers.cli.language_detector`
- `skill_seekers.cli.language_detector`
- `skill_seekers.cli.language_detector`
- `skill_seekers.cli.language_detector`
- `skill_seekers.cli.language_detector`
- `skill_seekers.cli.pdf_extractor_poc`
- `skill_seekers.cli.pdf_extractor_poc`
- `skill_seekers.cli.pdf_extractor_poc`
- `skill_seekers.cli.pdf_extractor_poc`
- `skill_seekers.cli.pdf_extractor_poc`
- `skill_seekers.cli.pdf_extractor_poc`
- `fitz`
- `unittest.mock`
- `fitz`
- `unittest.mock`
- `fitz`
- `unittest.mock`
- `fitz`
- `unittest.mock`
- `fitz`

**Setup Required:**
```python
if not PYMUPDF_AVAILABLE:
    self.skipTest('PyMuPDF not installed')
from skill_seekers.cli.pdf_extractor_poc import PDFExtractor
self.PDFExtractor = PDFExtractor
```

## Step-by-Step Guide

### Step 1: 'Test Scala detection'

```python
'Test Scala detection'
```

### Step 2: Assign extractor = self.PDFExtractor.__new__(...)

```python
extractor = self.PDFExtractor.__new__(self.PDFExtractor)
```

### Step 3: Assign extractor.language_detector = LanguageDetector(...)

```python
extractor.language_detector = LanguageDetector(min_confidence=0.15)
```

### Step 4: Assign code = '\n        case class Person(name: String, age: Int)\n\n        object Main extends App {\n          val person = Person("Alice", 30)\n          person match {\n            case Person(n, a) if a >= 18 => println(s"Adult: $n")\n            case _ => println("Minor")\n          }\n        }\n        '

```python
code = '\n        case class Person(name: String, age: Int)\n\n        object Main extends App {\n          val person = Person("Alice", 30)\n          person match {\n            case Person(n, a) if a >= 18 => println(s"Adult: $n")\n            case _ => println("Minor")\n          }\n        }\n        '
```

### Step 5: Assign unknown = extractor.detect_language_from_code(...)

```python
language, confidence = extractor.detect_language_from_code(code)
```

### Step 6: Call self.assertEqual()

```python
self.assertEqual(language, 'scala')
```

### Step 7: Call self.assertGreater()

```python
self.assertGreater(confidence, 0.7)
```


## Complete Example

```python
# Setup
if not PYMUPDF_AVAILABLE:
    self.skipTest('PyMuPDF not installed')
from skill_seekers.cli.pdf_extractor_poc import PDFExtractor
self.PDFExtractor = PDFExtractor

# Workflow
'Test Scala detection'
extractor = self.PDFExtractor.__new__(self.PDFExtractor)
from skill_seekers.cli.language_detector import LanguageDetector
extractor.language_detector = LanguageDetector(min_confidence=0.15)
code = '\n        case class Person(name: String, age: Int)\n\n        object Main extends App {\n          val person = Person("Alice", 30)\n          person match {\n            case Person(n, a) if a >= 18 => println(s"Adult: $n")\n            case _ => println("Minor")\n          }\n        }\n        '
language, confidence = extractor.detect_language_from_code(code)
self.assertEqual(language, 'scala')
self.assertGreater(confidence, 0.7)
```

## Next Steps


---

*Source: test_pdf_extractor.py:174 | Complexity: Intermediate | Last updated: 2026-02-14*